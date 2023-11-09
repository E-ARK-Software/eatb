# eatb - eArchiving Tool Box

## About

The archiving tool box is a suite of tools for the creation of information packages for archival purposes. The archival
information package must follow the structure defined by the E-ARK specification for information packages (CSIP 
available at https://earkcsip.dilcis.eu).

    ,-------------------------------------------------------.
    | Information package {Persistent Unique Identifier}    |
    |-------------------------------------------------------|
    | - metadata/                                           | <--- Descriptive metadata
    |     - EAD.xml                                          |
    |-------------------------------------------------------|
    | - representations/                                    | <--- Representations
    |     - text_representation/                            | 
    |         - data/                                       |
    |             - file1.txt                               |
    |             - file2.txt                               |
    |         - metadata/                                   |
    |         - documentation/                              |
    |     - csv_representation/                             | 
    |         - data/                                       |
    |             - file1.csv                               |
    |             - file2.csv                               |
    |         - metadata/                                   |
    |         - documentation/                              |
    |-------------------------------------------------------|
    | - schemas/                                            | <--- Schema files for validation
    |     - IP_CS_mets.xsd                                  |
    |     - premis-v2-2.xsd                                 |
    |     - xlink.xsd                                       |
    |-------------------------------------------------------|
    | - METS.xml                                            | <--- Root METS file (structural metadata)
    `-------------------------------------------------------'

The archiving toolbox allows creating an information package based on files which are organized according to the
structure of a CSIP. It will validate the structure and create METS metadata representing the structure of the package
and PREMIS metadata which allows recording the provenance of it. 

    myip
    ├── metadata
    │   └── dc.xml
    └── representations
        └── repr1
            └── data
                └── test.txt


    myip
    ├── metadata
    │   ├── dc.xml
    │   └── preservation
    │       └── premis.xml
    ├── METS.xml
    └── representations
        └── repr1
            ├── data
            │   └── test.txt
            ├── metadata
            │   └── preservation
            │       └── premis.xml
            └── METS.xml

## Installation

Install python packages (in virtual environment):

    pip install -r requirements.txt

## Use

Create information packages:

    python3 eatb/package_creator.py -n <packagename> -d <package_directory> -t SIP
    
## Unit tests

Install py.test

    pip install -U pytest

Run tests:

    py.test tests
