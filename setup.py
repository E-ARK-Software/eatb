import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eatb",
    version="0.1.8",
    author="E-ARK Foundation",
    author_email="admin@e-ark-foundation.eu",
    license='MIT',
    description="A suite of tools for the creation of information packages for archival purposes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.e-ark-foundation.eu/e-ark-software-eatb",
    packages=setuptools.find_packages(),
    package_data={'': []},
    data_files=[
        ("settings",  ["settings/settings.cfg", "settings/default_commands.cfg"]),
        ("",  ["logging_config.ini"])
    ],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)
