#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test storage module"""
import os
import shutil
import json
import unittest
from eatb import ROOT
from eatb.utils import randomutils
from eatb.storage import update_storage_with_differences
from eatb.storage import write_inventory_from_directory

OCFL_STORAGE_DIR = os.path.join(ROOT, 'tests/test_resources/ocfl-storage/')
EXAMPLE_WORKING_DIR = os.path.join(OCFL_STORAGE_DIR, 'working-dir')
TMP_DIRECTORY = '/tmp/temp-' + randomutils.randomword(10)
TMP_WORKING_DIRECTORY = TMP_DIRECTORY + 'workingdir'
TMP_AIP_DIRECTORY = TMP_DIRECTORY + 'aipdir'
ADDITIONAL_FILE = 'additionalfile.txt'
ADDITIONAL_FILE_PATH = os.path.join(OCFL_STORAGE_DIR, ADDITIONAL_FILE)

class TestOcflStorage(unittest.TestCase):
    """Test storage functions"""
    @classmethod
    def setUpClass(cls):
        try:
            # Ensure the repository storage directory exists
            if not os.path.exists(TMP_DIRECTORY):
                os.makedirs(TMP_DIRECTORY)
            if not os.path.exists(TMP_WORKING_DIRECTORY):
                os.makedirs(TMP_WORKING_DIRECTORY)
            if not os.path.exists(TMP_AIP_DIRECTORY):
                os.makedirs(TMP_AIP_DIRECTORY)

            # Copy the content from test_repo to repository_storage_dir
            for item in os.listdir(EXAMPLE_WORKING_DIR):
                source_path = os.path.join(EXAMPLE_WORKING_DIR, item)
                destination_path = os.path.join(TMP_WORKING_DIRECTORY, item)

                if os.path.isdir(source_path):
                    print(f"Copy directory from '{source_path}' to '{destination_path}'.")
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True) 
                else:
                    print(f"Copy file from '{source_path}' to '{destination_path}'.")
                    shutil.copy2(source_path, destination_path)  

            # Verify and log success
            print(f"Copied contents from '{EXAMPLE_WORKING_DIR}' to '{TMP_WORKING_DIRECTORY}'.")

        except Exception as e:
            raise RuntimeError("Error setting up test") from e

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TMP_DIRECTORY)

    def test_1_tmp_working_dir_file_access(self):
        """Test file access in temporary package"""
        self.assertTrue(os.path.exists(os.path.join(TMP_WORKING_DIRECTORY, "METS.xml")))

    def test_2_store_first_version(self):
        """Test write storage"""
        # Define version and storage directories
        package_name = "example.aip"
        working_dir = TMP_WORKING_DIRECTORY
        data_dir = os.path.join(TMP_AIP_DIRECTORY, "data")
        previous_version = "v00000"
        new_version = "v00001"
        new_version_target_dir = os.path.join(data_dir, new_version)
        os.makedirs(new_version_target_dir, exist_ok=True)
        inventory_path = os.path.join(data_dir, "inventory.json")
        excludes = [f"{package_name}.tar", f"{package_name}.xml"]
        changed_files, deleted_files = update_storage_with_differences(
            working_dir, new_version_target_dir, previous_version, inventory_path, exclude_files=excludes
        )
        # Update inventory
        print(f"Updating OCFL inventory for version {new_version}")
        write_inventory_from_directory(
            identifier="urn:uuid:d695500b-0209-4c06-bea6-8fdd52c6db22",
            version=new_version,
            data_dir=data_dir,
            action="ingest",
            metadata={"added": changed_files, "removed": deleted_files},
        )
    
    def test_3_additional_file_to_working_dir(self):
        """Test adding additional file to temporary working dir"""
        # make sure the additional file exists
        self.assertTrue(os.path.exists(ADDITIONAL_FILE_PATH))
        additional_file_target_dir = os.path.join(TMP_WORKING_DIRECTORY, "representations/a87c22b3-af5a-4c3c-8463-4d6eab95439c/data/")
        shutil.copy2(ADDITIONAL_FILE_PATH, additional_file_target_dir)  
        # make sure the additional file was added to the working directory
        self.assertTrue(os.path.exists(os.path.join(additional_file_target_dir, ADDITIONAL_FILE)))

    
    def test_4_additional_file_to_working_dir(self):
        """Test write new version storage"""
        # Define version and storage directories
        package_name = "example.aip"
        working_dir = TMP_WORKING_DIRECTORY
        data_dir = os.path.join(TMP_AIP_DIRECTORY, "data")
        previous_version = "v00001"
        new_version = "v00002"
        new_version_target_dir = os.path.join(data_dir, new_version)
        os.makedirs(new_version_target_dir, exist_ok=True)
        inventory_path = os.path.join(data_dir, "inventory.json")
        excludes = [f"{package_name}.tar", f"{package_name}.xml"]
        changed_files, deleted_files = update_storage_with_differences(
            working_dir, new_version_target_dir, previous_version, inventory_path, exclude_files=excludes
        )
        # Update inventory
        print(f"Updating OCFL inventory for version {new_version}")
        write_inventory_from_directory(
            identifier="urn:uuid:d695500b-0209-4c06-bea6-8fdd52c6db22",
            version=new_version,
            data_dir=data_dir,
            action="ingest",
            metadata={"added": changed_files, "removed": deleted_files},
        )
        """Test if the specified file is present under 'versions/v00002/added'"""
        # Load the inventory.json file
        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory = json.load(f)

        # Check if the specific entry is in the 'added' list under 'v00002'
        added_files = inventory.get("versions", {}).get("v00002", {}).get("added", [])
        self.assertIn("representations/a87c22b3-af5a-4c3c-8463-4d6eab95439c/data/additionalfile.txt", added_files)



if __name__ == '__main__':
    unittest.main()
