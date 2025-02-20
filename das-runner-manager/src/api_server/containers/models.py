from pydantic import BaseModel
from typing import Dict, Optional

class DockerContainerRunRequest(BaseModel):
    image: str
    name: str
    volumes: Dict[str, Dict[str, str]] = {}
    environment: Dict[str, str] = {}
    privileged: bool = False
    detach: bool = True
    network_mode: Optional[str] = None
    network: Optional[str] = None
    tmpfs: Optional[Dict[str, str]] = None
    hostname: Optional[str] = None
    restart_policy: Optional[Dict[str, str]]
