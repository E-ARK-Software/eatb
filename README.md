# eatb - eArchiving Tool Box ![Build](https://github.com/E-ARK-Software/eatb/actions/workflows/python-app.yml/badge.svg?sanitize=true) ![Coverage](https://raw.githubusercontent.com/E-ARK-Software/eatb/master/coverage_badge.svg?sanitize=true) 

## About

The archiving tool box is a suite of tools for the creation of information packages for archival purposes. The archival
information package must follow the structure and comply with metadata requirements defined by the E-ARK specification 
for information packages (CSIP available at https://earkcsip.dilcis.eu).

## Quick Start

### Pre-requisites

Python 3.7+ is required.

### Install latest package version from the Python Package Index (PyPi)

    pip install eatb

### Install from GitHub source code

Clone the project move into the directory:

    git clone https://github.com/E-ARK-Software/eatb.git
    cd eatb

Set up a local virtual environment:

    virtualenv -p python3 venv
    source venv/bin/activate

Update pip and install the application:

    pip install -U pip
    pip install .

### Use

Create information packages:

    python3 eatb/package_creator.py -n <packagename> -d <package_directory> -t SIP

The tool `eatb` allows creating an E-ARK information packages based on files which are organized according to the basic
file system structure as defined by the CSIP (https://earkcsip.dilcis.eu). 

A minimal example is the following information package data structured according to CSP with one data file `test.txt`
as representation `repr1` and an `EAD.xml` metadata file.

    myip
    ├── metadata
    │   └── EAD.xml
    └── representations
        └── repr1
            └── data
                └── test.txt

Using the packaging command, the structural and preservation data, `METS.xml` and `premis.xml` is added to the package:

    myip
    ├── metadata
    │   ├── dc.xml
    │   └── preservation
    │       └── premis.xml
    ├── METS.xml
    └── representations
        └── repr1
            ├── data
            │   └── test.txt
            ├── metadata
            │   └── preservation
            │       └── premis.xml
            └── METS.xml

A more complete example with two representations is shown in the example below.

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
    |     - premis-v3-0.xsd                                 |
    |     - xlink.xsd                                       |
    |-------------------------------------------------------|
    | - METS.xml                                            | <--- Root METS file (structural metadata)
    `-------------------------------------------------------'
 
## Set up a development environment for the project

### Get source code and create virtual environment using `pip`

Clone the project and move into the directory:

    git clone https://github.com/E-ARK-Software/eatb.git
    cd eatb

Set up a local virtual environment:

    virtualenv -p python3 venv
    source venv/bin/activate

### Unit tests

Install py.test

    pip install -U pytest

Run tests:

    py.test tests
