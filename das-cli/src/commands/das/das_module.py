from typing import List
from common import Module

from .das_ubuntu_advanced_packaging_tool import DasUbuntuAdvancedPackagingTool
from .das_cli import DasCli


class DasModule(Module):
    _instance = DasCli

    def __init__(self):
        super().__init__()

        self._dependecy_injection = [
            (
                DasUbuntuAdvancedPackagingTool,
                self._das_ubuntu_advanced_packaging_tool_factory,
            ),
        ]

    def _das_ubuntu_advanced_packaging_tool_factory(self) -> DasUbuntuAdvancedPackagingTool:
        return DasUbuntuAdvancedPackagingTool(package_name="das-toolbox")
