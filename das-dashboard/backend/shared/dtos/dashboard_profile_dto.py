from fastapi import Form, UploadFile, File
from pydantic import BaseModel

class DashboardProfileDto(BaseModel):
    sshUsername: str
    sshKeyFile: UploadFile

    @classmethod
    def as_form(
        cls,
        sshUsername: str = Form(..., alias="sshUsername"),
        sshKeyFile: UploadFile = File(..., alias="sshKeyFile")
    ):
        return cls(
            sshUsername=sshUsername,
            sshKeyFile=sshKeyFile
        )