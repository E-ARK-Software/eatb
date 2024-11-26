#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import shutil
import hashlib
from typing import List, Tuple, Dict
from collections import defaultdict
from datetime import datetime
from subprocess import check_output

from eatb.cli import CliCommand, CliCommands
from eatb import VersionDirFormat


def get_previous_version_series(current_version: str, version_format: str = VersionDirFormat) -> list:
    """
    Generate a list of previous version strings up to (excluding) the given current version.

    Parameters:
        current_version (str): The current version string, e.g., "v00002".
        version_format (str): The format string for the version, e.g., 'v%05d'.

    Returns:
        list: A list of previous version strings in the series.

    Example usage:
        print(get_version_series("v00001"))  # Output: []
        print(get_version_series("v00002"))  # Output: ['v00001']
        print(get_version_series("v00005"))  # Output: ['v00001', 'v00002', 'v00003', 'v00004']
    """
    # Extract the numeric part of the current version
    try:
        current_number = int(current_version[1:])
    except ValueError as e:
        raise ValueError("Invalid version format. Must match the version_format, e.g., 'v%05d'.") from e

    # Generate all previous versions
    return [version_format % i for i in range(1, current_number)]


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


def write_inventory_from_directory(
        identifier: str, 
        version: str, 
        data_dir: str, 
        action: str, 
        metadata: Dict = None
) -> bool:
    """
    Generates or updates an inventory based on the contents of a specified directory.

    Parameters:
        identifier (str): 
            A unique identifier for the inventory or the dataset being processed. 
            This could be a package ID, dataset name, or other unique identifier.

        version (str): 
            The version label for the inventory. This allows tracking changes 
            across different versions of the data.

        data_dir (str): 
            The path to the directory containing the files to be inventoried. 
            This directory is scanned recursively to collect file information.

        action (str): 
            Specifies the action to be performed. Examples might include:
            - `"create"`: Create a new inventory for the given directory.
            - `"update"`: Update an existing inventory with the latest changes.
            - `"validate"`: Validate the inventory against the current directory state.

        metadata (Dict, optional): 
            A dictionary containing additional metadata to be associated with the inventory. 
            Examples include:
            - Creation date
            - Author information
            - Custom tags
            Defaults to `None`, meaning no additional metadata is included.

    Returns:
        bool: 
            `True` if the inventory was successfully written or updated, 
            `False` if the operation failed.

    Raises:
        ValueError: If invalid parameters (e.g., unsupported `action`) are provided.
        FileNotFoundError: If the specified `data_dir` does not exist.
        IOError: If there is an issue writing the inventory file.

    Example:
        success = write_inventory_from_directory(
            identifier="dataset123",
            version="v1.0",
            data_dir="/path/to/data",
            action="create",
            metadata={"author": "Name of Author", "created_at": "2024-11-26"}
        )
        if success:
            print("Inventory successfully written.")
        else:
            print("Failed to write inventory.")
    """
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

    # Collect existing files from all previous versions
    existing_files = {}
    for prev_version, prev_data in inventory["versions"].items():
        for hash_val, paths in prev_data["state"].items():
            for path in paths:
                existing_files[f"{prev_version}/{path}"] = hash_val

    # Process files in the version directory
    version_dir = os.path.join(data_dir, version)
    for subdir, _, files in os.walk(version_dir):
        for file in files:
            file_path = os.path.join(subdir, file)
            relative_path = os.path.relpath(file_path, version_dir)
            full_ocfl_path = f"{version}/{relative_path}"  # Full path in the current version
            hashes = compute_file_hashes(file_path)

            if any(
                existing_path.endswith(relative_path) and existing_files[existing_path] == hashes["sha512"]
                for existing_path in existing_files
            ):
                print(f"Skipping {file_path} as it already exists")
                continue

            for algo, hash_val in hashes.items():
                inventory["fixity"][algo][hash_val].append(full_ocfl_path)

                # Ensure the relative_path is added only once to manifest
                if full_ocfl_path not in inventory["manifest"][hashes["sha512"]]:
                    inventory["manifest"][hashes["sha512"]].append(full_ocfl_path)

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

    return os.path.exists(inventory_path) and os.path.exists(inventory_path)


def update_storage_with_differences(
        working_dir: str, new_version_target_dir: str, previous_versions: List[str],
        inventory_path: str, exclude_files: List[str] = None
) -> Tuple[List[str], List[str]]:
    """
    Copies only new or modified files to the storage directory and identifies deleted files.

    Parameters:
        working_dir (str): 
            The directory containing the current version of the files that need to be compared 
            with previous versions. This is the source directory for the operation.

        new_version_target_dir (str): 
            The target directory where new or modified files will be copied. 
            This represents the storage location for the updated version.

        previous_versions (List[str]): 
            A list of version identifiers (version tags, e.g., v00001) that represent 
            the prior states of the files. These versions are used to determine whether 
            files have changed, been added, or deleted.

        inventory_path (str): 
            The path to the inventory file (in JSON format), which contains metadata about 
            the files in all previous versions. This file is used to track file states across 
            versions (e.g., hashes and paths).

        exclude_files (List[str], optional): 
            A list of filenames to be excluded from the comparison and copying process. 
            These files will be ignored even if they differ between versions. 
            Defaults to `None`, meaning no files are excluded.

    Returns:
        Tuple[List[str], List[str]]: 
            A tuple containing:
            - `added_or_changed` (List[str]): A list of relative paths for files that were 
              either added or modified in the `working_dir` compared to the `previous_versions`.
            - `deleted_files` (List[str]): A list of relative paths for files that were 
              present in the `previous_versions` but are no longer in the `working_dir`.

    Example:
        added, deleted = update_storage_with_differences(
            working_dir="/path/to/current",
            new_version_target_dir="/path/to/storage",
            previous_versions=["v00001", "v00002"],
            inventory_path="/path/to/inventory.json",
            exclude_files=["tempfile.txt", "debug.log"]
        )
    """
    added_or_changed = []
    deleted_files = []
    previous_files = {}

    assert isinstance(previous_versions, list), \
        "param 'previous_versions' must be of type list"

    assert not exclude_files or isinstance(exclude_files, list), \
        "param 'exclude_files' must be of type list"

    # Load inventory to get the state of all previous versions
    if os.path.exists(inventory_path):
        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory = json.load(f)
            for prev_version in previous_versions:
                version_state = inventory["versions"].get(prev_version, {}).get("state", {})
                for hash_val, paths in version_state.items():
                    for path in paths:
                        previous_files[path] = hash_val

    # Compare files in the working directory with all previous versions
    for subdir, _, files in os.walk(working_dir):
        for file in files:
            source_file = os.path.join(subdir, file)
            relative_path = os.path.relpath(source_file, working_dir)
            target_file = os.path.join(new_version_target_dir, relative_path)
            os.makedirs(os.path.dirname(target_file), exist_ok=True)

            # Compute hash for the current file
            current_hash = compute_file_hashes(source_file)["sha512"]
            #Files which exist in previous versions with the same hash do not get copied
            if any(
                existing_path.endswith(relative_path) and previous_files[existing_path] == current_hash
                for existing_path in previous_files
            ):
                print(f"Skipping {source_file} as it already exists in previous versions")
                continue

            # Check if the file is new or has changed
            if (relative_path not in previous_files or previous_files[relative_path] != current_hash) and file not in (exclude_files or []):
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
