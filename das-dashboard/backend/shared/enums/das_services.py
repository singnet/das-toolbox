from enum import Enum

class DASServices(Enum):

    ATOMDB = {
        "pattern": ["das-cli-mongodb", "das-cli-redis", "das-cli-morkdb", "das-morkdb"],
        "command": "db",
        "requires_peer": False,
    }

    QUERY_AGENT = {
        "pattern": "das-query-engine",
        "command": "query-agent",
        "requires_peer": False,
    }

    INFERENCE_AGENT = {
        "pattern": "das-inference-agent",
        "command": "inference-agent",
        "requires_peer": True,
    }

    EVOLUTION_AGENT = {
        "pattern": "das-evolution-agent",
        "command": "evolution-agent",
        "requires_peer": True,
    }

    LINK_CREATION_AGENT = {
        "pattern": "das-link-creation-agent",
        "command": "link-creation-agent",
        "requires_peer": True,
    }

    ATTENTION_BROKER = {
        "pattern": "das-attention-broker",
        "command": "attention-broker",
        "requires_peer": False,
    }

    CONTEXT_BROKER = {
        "pattern": "das-context-broker",
        "command": "context-broker",
        "requires_peer": True,
    }

    ATOMDB_BROKER = {
        "pattern": "das-atomdb-broker",
        "command": "atomdb-broker",
        "requires_peer": False,
    }

    @classmethod
    def from_container(cls, container_name: str):

        for service in cls:

            pattern = service.value["pattern"]

            if container_name in pattern:
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