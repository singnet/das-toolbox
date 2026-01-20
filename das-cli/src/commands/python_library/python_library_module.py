from typing import List

from common import Module

from .python_library_cli import PythonLibraryCli


class PythonLibraryModule(Module):
    _instance = PythonLibraryCli
    _dependency_list: List = []
