from setuptools import find_packages, setup

from config.config import get_config

setup(
    name="das-cli",
    version=get_config("VERSION"),
    packages=find_packages(),
    scripts=["das_cli.py"],
    entry_points={
        "console_scripts": [
            "das-cli=das_cli:das_cli",
        ],
    },
)
