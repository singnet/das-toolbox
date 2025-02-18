from pydantic import BaseModel
from typing import Dict

class DockerContainerRunRequest(BaseModel):
    image: str
    name: str
    volumes: Dict[str, str] = {}
    environment: Dict[str, str] = {}
    privileged: bool = False
    detach: bool = True
