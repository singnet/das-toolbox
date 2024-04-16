from setuptools import setup, find_packages

setup(
    name="das-cli",
    version="1.0",
    packages=find_packages(),
    scripts=["das_cli.py"],
    entry_points={
        "console_scripts": [
            "das-cli=das_cli:das_cli",
        ],
    },
)
