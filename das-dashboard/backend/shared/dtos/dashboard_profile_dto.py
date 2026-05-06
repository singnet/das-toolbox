from pydantic import BaseModel, Field

class DashboardProfileDto(BaseModel):
    profile_username: str = Field(alias="profileName")
    profile_ssh_username: str = Field(alias="sshUsername")
    profile_ssh_keypath: str = Field(alias="sshKeyPath")