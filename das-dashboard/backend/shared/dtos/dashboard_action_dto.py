from pydantic import BaseModel

class DashboardActionDTO(BaseModel):
    target_ip : str
    target_port : int
    target_username : str
    target_ssh_file_path: str
    target_service : str


    