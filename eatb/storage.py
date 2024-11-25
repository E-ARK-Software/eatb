#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import shutil
import hashlib
from collections import defaultdict
from datetime import datetime
from subprocess import check_output

from eatb.cli import CliCommand, CliCommands


def get_hashed_filelist(strip_path_part, directory, commands=CliCommands()):
    """
    e.g. get_hashed_filelist("/home/user/", "/home/user/test")
    :param commands:
    :param strip_path_part: part of the path to be removed for the key
    :param directory: directory for which the hashed file list is to be created
    :return: hashed file list
    """
    cli_command = CliCommand("summainstdout", commands.get_command_template("summainstdout"))
    command = cli_command.get_command(dict(package_dir=directory))
    summain_out = check_output(command)
    json_summain_out = json.loads(summain_out)
    result = {}
    for entry in json_summain_out:
        if "SHA256" in entry:
            key = entry['Name'].lstrip(strip_path_part)
            result[key] = {"hash": entry['SHA256'], "path": entry["Name"]}
    return result


def compute_sha512(file_path):
    """
    Computes the SHA-512 hash of a file.
    """
    sha512_hash = hashlib.sha512()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):  # Read in 8KB chunks
            sha512_hash.update(chunk)
    return sha512_hash.hexdigest()


def compute_md5(file_path):
    """
    Computes the MD5 hash of a file.
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):  # Read in 8KB chunks
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def compute_file_hashes(file_path):
    """
    Computes multiple hashes (e.g., SHA-512 and MD5) for a file and returns them as a dictionary.
    """
    return {
        "sha512": compute_sha512(file_path),
        "md5": compute_md5(file_path),
    }


def get_sha512_hash(file_path):
    """Compute the SHA-512 hash of a file."""
    h = hashlib.sha512()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def write_inventory_from_directory(identifier, version, data_dir, action, metadata=None):
    """Write inventory"""
    if not os.path.exists(data_dir):
        raise ValueError(f"Data directory does not exist: {data_dir}")

    inventory_path = os.path.join(data_dir, "inventory.json")

    # Load or initialize the inventory
    if os.path.exists(inventory_path):
        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory = json.load(f)

        # Reinitialize fixity as defaultdict
        inventory["fixity"] = defaultdict(lambda: defaultdict(list), {
            algo: defaultdict(list, hash_dict) for algo, hash_dict in inventory.get("fixity", {}).items()
        })
        inventory["manifest"] = defaultdict(list, inventory.get("manifest", {}))
    else:
        inventory = {
            "digestAlgorithm": "sha512",
            "fixity": defaultdict(lambda: defaultdict(list)),
            "head": version,
            "id": identifier,
            "manifest": defaultdict(list),
            "type": "https://ocfl.io/1.1/spec/#inventory",
            "versions": {}
        }

    # Prepare version entry
    version_entry = {
        "created": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "message": action,
        "state": defaultdict(list),
        "added": metadata.get("added", []),
        "removed": metadata.get("removed", []),
    }

    # Process files in the version directory
    version_dir = os.path.join(data_dir, version)
    for subdir, _, files in os.walk(version_dir):
        for file in files:
            file_path = os.path.join(subdir, file)
            # Compute relative path directly from the version directory
            relative_path = os.path.relpath(file_path, version_dir)
            hashes = compute_file_hashes(file_path)

            for algo, hash_val in hashes.items():
                print(f"Adding: {algo}, {hash_val}, {relative_path}")
                inventory["fixity"][algo][hash_val].append(f"{version}/{relative_path}")

                # Ensure the relative_path is added only once to manifest
                if f"{version}/{relative_path}" not in inventory["manifest"][hashes["sha512"]]:
                    inventory["manifest"][hashes["sha512"]].append(f"{version}/{relative_path}")

                # Ensure the relative_path is added only once to state
                if relative_path not in version_entry["state"][hashes["sha512"]]:
                    version_entry["state"][hashes["sha512"]].append(relative_path)

    # Update inventory
    inventory["versions"][version] = version_entry
    inventory["head"] = version

    # Write updated inventory
    with open(inventory_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=4)

    # Write OCFL object declaration and checksum
    with open(os.path.join(data_dir, "0=ocfl_object_1.0"), "w", encoding="utf-8") as ocfl_file:
        ocfl_file.write("ocfl_object_1.0")
    inventory_hash = get_sha512_hash(inventory_path)
    with open(os.path.join(data_dir, "inventory.json.sha512"), "w", encoding="utf-8") as hash_file:
        hash_file.write(f"{inventory_hash} inventory.json")


def update_storage_with_differences(working_dir, new_version_target_dir, previous_version_existing_dir, inventory_path, exclude_files=None):
    """
    Copies only new or modified files to the storage directory and identifies deleted files.

    Returns:
        tuple: (list of added/changed files, list of deleted files)
    """
    added_or_changed = []
    deleted_files = []
    previous_files = {}

    assert not exclude_files or type(exclude_files) is list, \
        "param 'exclude_files' must be of type list"

    # Load inventory to get the state of the previous version
    if os.path.exists(inventory_path):
        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory = json.load(f)
            previous_version_state = inventory["versions"].get(previous_version_existing_dir, {}).get("state", {})
            for hash_val, paths in previous_version_state.items():
                for path in paths:
                    previous_files[path] = hash_val

    # Compare files in the working directory with the previous version
    for subdir, _, files in os.walk(working_dir):
        for file in files:
            source_file = os.path.join(subdir, file)
            relative_path = os.path.relpath(source_file, working_dir)
            target_file = os.path.join(new_version_target_dir, relative_path)
            os.makedirs(os.path.dirname(target_file), exist_ok=True)

            # Compute hash for the current file
            current_hash = compute_file_hashes(source_file)["sha512"]

            # Check if the file is new or has changed
            if (relative_path not in previous_files or previous_files[relative_path] != current_hash) and file not in exclude_files:
                # Check if the file already exists with the same content
                if not os.path.exists(target_file) or compute_file_hashes(target_file)["sha512"] != current_hash:
                    shutil.copy2(source_file, target_file)
                    added_or_changed.append(relative_path)

    # Identify deleted files
    current_files = {os.path.relpath(os.path.join(subdir, file), working_dir) for subdir, _, files in os.walk(working_dir) for file in files}
    for path in previous_files.keys():
        if path not in current_files:
            deleted_files.append(path)

    return added_or_changed, deleted_files
