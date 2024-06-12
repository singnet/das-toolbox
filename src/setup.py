from setuptools import setup, find_packages
from config.config import VERSION

setup(
    name="das-cli",
    version=VERSION,
    packages=find_packages(),
    scripts=["das-cli.py"],
    entry_points={
        "console_scripts": [
            "das-cli=das_cli:das_cli",
        ],
    },
)
