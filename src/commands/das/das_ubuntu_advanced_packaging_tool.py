import re
import subprocess
from typing import Tuple, Union


class DasError(Exception):
    ...  # noqa: E701


class DasNotFoundError(DasError):
    ...  # noqa: E701


class DasUbuntuAdvancedPackagingTool:
    def __init__(self, package_name) -> None:
        self.package_name = package_name

    @staticmethod
    def update_repository():
        try:
            subprocess.check_output(
                [
                    "apt",
                    "update",
                ],
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def get_package_version(self) -> Tuple[Union[None, str]]:
        try:
            output = subprocess.check_output(
                [
                    "apt-cache",
                    "policy",
                    self.package_name,
                ],
                stderr=subprocess.DEVNULL,
            )

            version_pattern = r"Installed:\s*(\d+\.\d+\.\d+)\n\s*Candidate:\s*(\d+\.\d+\.\d+)"

            matches = re.findall(version_pattern, output.decode("utf-8"))

            if matches:
                return matches[0]
            else:
                return None, None
        except subprocess.CalledProcessError:
            return None, None

    def install_package(self, version: Union[str, None]) -> None:
        self.update_repository()

        if version is None:
            subprocess.run(
                [
                    "apt",
                    "install",
                    "--only-upgrade",
                    f"{self.package_name}",
                    "-y",
                ],
                check=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
        else:
            subprocess.run(
                [
                    "apt",
                    "install",
                    "--only-upgrade",
                    "--allow-downgrades",
                    f"{self.package_name}={version}",
                    "-y",
                ],
                check=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )

        newer_version, _ = self.get_package_version()

        return newer_version
