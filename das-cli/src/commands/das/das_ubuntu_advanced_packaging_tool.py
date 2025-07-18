import re
import subprocess
from typing import Union


class DasPackageUpdateError(Exception):
    ...  # noqa: E701


class DasNotFoundError(DasPackageUpdateError):
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

    def get_package_version(self) -> Union[None, str]:
        try:
            output = subprocess.check_output(
                [
                    "apt-cache",
                    "policy",
                    self.package_name,
                ],
                stderr=subprocess.DEVNULL,
            ).decode("utf-8")

            match = re.search(r"Installed:\s*([\w\d.+~-]+)", output)

            if match:
                installed_version = match.group(1)
                return installed_version if installed_version != "(none)" else None

            return None
        except subprocess.CalledProcessError:
            return None

    def install_package(self, version: Union[str, None]) -> Union[str, None]:
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

        newer_version = self.get_package_version()

        return newer_version
