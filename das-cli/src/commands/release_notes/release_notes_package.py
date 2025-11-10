import re
from typing import Dict, List, Union

import requests

from common import remove_special_characters
from settings.config import RELEASE_NOTES_URL


class ReleaseNoteError(Exception):
    ...  # noqa: E701


class ReleaseNoteNotFound(ReleaseNoteError):
    ...  # noqa: E701


class Library:
    def __init__(self, name, version):
        self._name = self._get_mapped_name(name)
        self._version = version
        self._changelog = []

    def _get_mapped_name(self, name):
        name_map = {
            "hyperon-das": "hyperon-das",
            "hyperon-das-atomdb": "hyperon-das-atomdb",
            "FaaS functions": "das-serverless-functions",
            "MeTTa Parser": "das-metta-parser",
            "Toolbox das-cli": "das-toolbox",
        }
        return name_map.get(name, name)

    def get_version(self):
        return self._version

    def get_name(self):
        return self._name

    def add_to_changelog(self, item):
        self._changelog.append(item)

    def get_changelog(self):
        return "\n".join(self._changelog)


class ReleaseNotesPackage:
    def fetch_release_notes(self) -> Union[str, None]:
        response = requests.get(RELEASE_NOTES_URL)
        if response.status_code == 200:
            return response.text
        return None

    def _parse_version_line(self, line: str) -> Union[str, None]:
        version_pattern = r"## DAS Version (.+)"
        match = re.match(version_pattern, line)
        if match:
            return str(match.group(1).strip())
        return None

    def _parse_package_line(self, line: str):
        package_pattern = r"^####\s(.+)\s(\d+\.\d+\.\d+)$"
        match = re.match(package_pattern, line)
        if match:
            return Library(
                name=match.group(1).strip(),
                version=match.group(2).strip(),
            )
        return None

    def parse_release_notes(self, release_notes_content: str) -> Dict[str, List[Library]]:
        release_notes: Dict[str, List[Library]] = {}
        current_version: Union[str, None] = None
        current_package: Union[Library, None] = None

        for line in release_notes_content.splitlines():
            if line.startswith("## DAS Version "):
                current_version = self._parse_version_line(line)
                if current_version:
                    release_notes[current_version] = []
                    current_package = None
            elif current_version and remove_special_characters(line) != "":
                package_info = self._parse_package_line(line)
                if package_info:
                    if current_package:
                        release_notes[current_version].append(current_package)
                    current_package = package_info
                elif current_package:
                    current_package.add_to_changelog(line.strip())

        if current_package and current_version:
            release_notes[current_version].append(current_package)

        return release_notes

    def get_latest_release_notes(self) -> List[Library]:
        release_notes_content = self.fetch_release_notes()
        if release_notes_content:
            parsed_release_notes = self.parse_release_notes(release_notes_content)
            latest_version = max(parsed_release_notes.keys())

            return parsed_release_notes[latest_version]
        else:
            return []

    def get_release_notes(self, module: Union[str, None] = None) -> List[Library]:
        releases: List[Library] = []

        if module is None:
            module_name = module
            module_version = None
        else:
            module_name, module_version = module.split("=")

        release_notes_content = self.fetch_release_notes()
        if release_notes_content:
            parsed_release_notes = self.parse_release_notes(release_notes_content)

            for packages in parsed_release_notes.values():
                for package in packages:
                    if module_name == package.get_name():
                        if module_version is not None:
                            if module_version == package.get_version():
                                releases.append(package)
                        else:
                            releases.append(package)
        if len(releases) < 1:
            raise ReleaseNoteNotFound(f"Release note for {module} not found")

        return releases
