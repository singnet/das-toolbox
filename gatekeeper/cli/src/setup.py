from setuptools import find_packages, setup

from settings.config import VERSION

setup(
    name="gkctl",
    version=VERSION,
    packages=find_packages(),
    scripts=["gkctl.py"],
    entry_points={
        "console_scripts": [
            "gkctl=gkctl:gkctl",
        ],
    },
)
