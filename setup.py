import setuptools  # type: ignore[import-untyped]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rsp1570serial-pp81381",
    use_scm_version={
        "local_scheme": "dirty-tag",
    },  # For PyPi compliance
    setup_requires=["setuptools_scm"],
    author="Phil Porter",
    description="Rotel RSP-1570 processor asyncio RS-232 protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pp81381/rsp1570serial",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Terminals :: Serial",
        "Topic :: Home Automation",
        "Framework :: AsyncIO",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pyserial>=3.4",
        "pyserial-asyncio-fast>=0.11",
    ],
)
