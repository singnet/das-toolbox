from pydantic import BaseModel

class DashboardActionDTO(BaseModel):
    target_ip : str
    target_port : int
    target_ssh_file_path: str
    target_service : str


    