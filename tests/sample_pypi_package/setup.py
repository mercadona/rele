import setuptools

setuptools.setup(
    name="sample_pypi_package",
    version="0.0.1b0",
    author="",
    author_email="",
    description="This is a sample package.",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
