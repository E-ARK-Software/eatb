import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="earchivingtoolbox",
    version="0.1",
    author="Sven Schlarb",
    author_email="shsdev@posteo.net",
    license='MIT',
    description="A suite of tools for the creation of information packages for archival purposes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="github.com/eark-project/earchivingtoolbox",
    packages=setuptools.find_packages(),
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)
