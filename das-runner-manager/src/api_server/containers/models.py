from pydantic import BaseModel
from typing import Dict

class DockerContainerRunRequest(BaseModel):
    image: str
    name: str
    volumes: Dict[str, Dict[str, str]] = {}
    environment: Dict[str, str] = {}
    privileged: bool = False
    detach: bool = True
    network_mode: str = "bridge"
    network: str = None
