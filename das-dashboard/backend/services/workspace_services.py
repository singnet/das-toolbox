import os

from shared.internal.constants import WORKSPACE_METTA_OUTPUT, WORKSPACE_ROOT, DEFAULT_METTA_FILES_PATH


class WorkspaceServices:

    WORKSPACE_DIRS = (
        WORKSPACE_ROOT,
        WORKSPACE_METTA_OUTPUT,
        DEFAULT_METTA_FILES_PATH,
    )

    def ensure_workspace(self) -> None:
        for directory in self.WORKSPACE_DIRS:
            os.makedirs(directory, exist_ok=True)
