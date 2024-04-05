import subprocess
from typing import Union


class PackageService:
    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        try:
            subprocess.check_output(
                [
                    "dpkg",
                    "-s",
                    package_name,
                ],
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def install_package(package_name: str, version: Union[str, None]) -> None:
        if version is None:
            subprocess.run(
                [
                    "sudo",
                    "apt",
                    "install",
                    "--only-upgrade",
                    f"{package_name}",
                    "-y",
                ],
                check=True,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.run(
                [
                    "sudo",
                    "apt",
                    "install",
                    "--only-upgrade",
                    "--allow-downgrades",
                    f"{package_name}={version}",
                    "-y",
                ],
                check=True,
                stderr=subprocess.DEVNULL,
            )
