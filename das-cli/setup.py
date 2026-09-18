import sys
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from setuptools import find_packages, setup

CURRENT_PATH = Path(__file__).resolve().parent
SRC_PATH = CURRENT_PATH / "src"
DEFAULT_CONFIG_TARGET = SRC_PATH / "settings" / "config.json"

sys.path.insert(0, str(SRC_PATH))

from settings.__version__ import VERSION


def ensure_default_config_file() -> None:
    """
    Ensure default DAS config exists in this package at build time.

    Resolution order:
    1. DAS_SOURCE_DIR env var, if provided
    2. Local sibling repository ../das
    3. Temporary clone from DAS_REPO_URL / DAS_REPO_REF
    """

    source_dir = Path(
        os.environ.get("DAS_SOURCE_DIR")
        or str((CURRENT_PATH.parent.parent / "das").resolve())
    ).resolve()
    source_file = source_dir / "config" / "das.json"

    DEFAULT_CONFIG_TARGET.parent.mkdir(parents=True, exist_ok=True)

    if source_file.exists():
        shutil.copy2(source_file, DEFAULT_CONFIG_TARGET)
        return

    repo_url = os.environ.get("DAS_REPO_URL", "https://github.com/singnet/das.git")
    repo_ref = os.environ.get("DAS_REPO_REF", "master")

    with tempfile.TemporaryDirectory() as tmpdir:
        clone_dir = Path(tmpdir) / "das"
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                repo_ref,
                repo_url,
                str(clone_dir),
            ],
            check=True,
        )

        cloned_file = clone_dir / "config" / "das.json"
        if not cloned_file.exists():
            raise RuntimeError("Could not locate config/das.json in cloned DAS repository.")

        shutil.copy2(cloned_file, DEFAULT_CONFIG_TARGET)

def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def get_install_requirements():
    req_path = SRC_PATH / "requirements.txt"
    if not req_path.exists():
        return []
    return [r.strip() for r in read_text_file(req_path).splitlines() if r.strip() and not r.strip().startswith("#")]


LONG_DESCRIPTION = read_text_file(CURRENT_PATH / "README.md") or read_text_file(CURRENT_PATH / "README.rst")

# Keep pip package config in sync with DAS source without maintaining a duplicate file.
ensure_default_config_file()

setup(
    name="das-cli",
    version=VERSION,
    description="Command-line tools and utilities for working with DAS",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Rafael Levi",
    author_email="rafaellevi@singularitynet.io",
    url="https://github.com/singnet/das-toolbox",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=("tests", "tests.*")),
    package_data={
        "settings": ["config.json"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "das-cli=das_cli:das_cli",
        ],
    },
    py_modules=["das_cli"],
    install_requires=get_install_requirements(),
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: CLI",
    ],
    keywords="das cli tooling singnet",
    project_urls={
        "Source": "https://github.com/singnet/das-toolbox",
        "Bug Tracker": "https://github.com/singnet/das-toolbox/issues",
        "Changelog": "https://github.com/singnet/das-toolbox/blob/master/CHANGELOG",
    },
)
