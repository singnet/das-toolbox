from pydantic import BaseModel

class NetworkCreateRequest(BaseModel):
    network_name: str
    driver: str = "bridge"

class AttachNetworkRequest(BaseModel):
    container_name: str
