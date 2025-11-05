from pathlib import Path
from setuptools import find_packages, setup

from src.settings.config import VERSION


CURRENT_PATH = Path(__file__).resolve().parent
SRC_PATH = CURRENT_PATH / "src"


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
