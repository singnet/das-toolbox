import re
import subprocess

import requests


class PackageError(Exception): ...


class PackageNotFoundError(PackageError): ...


class PythonLibraryPackage:
    def get_all_versions_from_pypi(self, package_name):
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        if response.status_code == 200:
            data = response.json()
            return list(data["releases"].keys())
        return []

    def get_all_major_minor_versions_from_pypi(self, package_name, show_patches=False):
        all_versions = self.get_all_versions_from_pypi(package_name)
        return self.extract_versions(all_versions, show_patches)

    def get_latest_version(self, package_name):
        url = f"https://pypi.org/pypi/{package_name}/json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data["info"]["version"]
        except requests.exceptions.RequestException as e:
            raise PackageNotFoundError(
                f"Error while fetching the latest version of the package '{package_name}': {e}"
            )

    def extract_versions(self, versions, show_patches=False):
        filtered_versions = set()
        for version in versions:
            if show_patches:
                filtered_versions.add(version)
            else:
                match = re.match(r"^(\d+\.\d+)", version)
                if match:
                    filtered_versions.add(match.group(1))
        return sorted(filtered_versions)

    def get_version(self, package_name):
        try:
            output = subprocess.check_output(
                ["pip", "show", package_name],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            version_line = re.search(r"^Version:\s*(.*)$", output, re.MULTILINE)
            if version_line:
                return version_line.group(1).strip()
            else:
                raise PackageNotFoundError(
                    f"Version information not found for package '{package_name}'."
                )
        except subprocess.CalledProcessError as e:
            raise PackageNotFoundError(f"Package '{package_name}' is not installed.")

    def update_version(self, package_name, version=None):
        self.get_version(package_name)

        pypi_package = f"{package_name}=={version}" if version is not None else package_name

        try:
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "--quiet",
                    pypi_package,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except subprocess.CalledProcessError:
            raise PackageError(
                f"Failed to update package {package_name}. Please verify if the provided version exists or ensure the package name is correct."
            )
