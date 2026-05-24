from enum import Enum
import re


class DASServices(Enum):

    ATOMDB = {
        "pattern": r"das-(mongodb|redis|mork)",
        "command": "db",
        "requires_peer": False,
    }

    QUERY_AGENT = {
        "pattern": r"das-query-engine",
        "command": "query-agent",
        "requires_peer": False,
    }

    INFERENCE_AGENT = {
        "pattern": r"das-inference-agent",
        "command": "inference-agent",
        "requires_peer": True,
    }

    EVOLUTION_AGENT = {
        "pattern": r"das-evolution-agent",
        "command": "evolution-agent",
        "requires_peer": True,
    }

    LINK_CREATION_AGENT = {
        "pattern": r"das-link-creation-agent",
        "command": "link-creation-agent",
        "requires_peer": True,
    }

    ATTENTION_BROKER = {
        "pattern": r"das-attention-broker",
        "command": "attention-broker",
        "requires_peer": False,
    }

    CONTEXT_BROKER = {
        "pattern": r"das-context-broker",
        "command": "context-broker",
        "requires_peer": True,
    }

    ATOMDB_BROKER = {
        "pattern": r"das-atomdb-broker",
        "command": "atomdb-broker",
        "requires_peer": False,
    }

    @classmethod
    def from_container(cls, container_name: str):

        for service in cls:

            pattern = service.value["pattern"]

            if re.search(pattern, container_name):
                return service

        raise ValueError(
            f"Unknown container name: {container_name}"
        )
    
    @classmethod
    def from_command(cls, command_name : str):

        for service in cls:

            if command_name in service.value["command"]:
                return service
            
        raise ValueError(
            f"Unknown command name: {command_name}"
        )