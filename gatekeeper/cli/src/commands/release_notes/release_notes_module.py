from typing import List

from common import Module

from .release_notes_cli import ReleaseNotesCli


class ReleaseNotesModule(Module):
    _instance = ReleaseNotesCli
    _dependecy_injection: List = []
