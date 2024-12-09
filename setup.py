import setuptools

# Read README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read dependencies from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="eatb",
    version="0.2.9",
    author="E-ARK Foundation",
    author_email="admin@e-ark-foundation.eu",
    license='MIT',
    description="A suite of tools for the creation of information packages for archival purposes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.e-ark-foundation.eu/e-ark-software-eatb",
    packages=setuptools.find_packages(),
    package_data={'eatb': ["*.ini", "**/*.cfg", "**/**/*.xsd", "**/*.xml"]},
    zip_safe=False,
    install_requires=requirements, 
    classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: System :: Archiving',
    ],

)
