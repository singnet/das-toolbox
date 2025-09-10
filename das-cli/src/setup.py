from setuptools import find_packages, setup

from settings.config import VERSION

# Runtime dependencies (excluding dev dependencies)
install_requires = [
    "Click==8.1.6",
    "docker==7.1.0",
    "distro==1.9.0",
    "click-man==0.4.1",
    "fabric==3.2.2",
    "cryptography==36.0.2",
    "paramiko==3.4.0",
    "pyyaml==6.0.1",
    "injector==0.21.0",
]

setup(
    name="das-cli",
    version=VERSION,
    description="CLI tool for managing Distributed Atomspace (DAS) services",
    long_description=open("../README.md").read(),
    long_description_content_type="text/markdown",
    author="SingularityNET",
    author_email="info@singularitynet.io",
    url="https://github.com/singnet/das-toolbox",
    packages=find_packages(),
    scripts=["das_cli.py"],
    install_requires=install_requires,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "console_scripts": [
            "das-cli=das_cli:das_cli",
        ],
    },
)
