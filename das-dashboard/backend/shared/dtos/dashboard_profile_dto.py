from pydantic import BaseModel

class DashboardProfileDto(BaseModel):
    profile_username : str
    profile_ssh_username : str
    profile_ssh_keypath : str