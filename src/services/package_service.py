import subprocess
from typing import Union


class PackageService:
    @staticmethod
    def is_ubuntu():
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.strip().split("=")[1].strip('"') == "ubuntu"
            return False
        except FileNotFoundError:
            return False

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
    def get_version(package_name: str) -> str:
        try:
            output = subprocess.check_output(["dpkg", "-s", package_name], text=True)
            for line in output.split("\n"):
                if line.startswith("Version:"):
                    return line.split(":")[1].strip()
        except subprocess.CalledProcessError:
            return None

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
