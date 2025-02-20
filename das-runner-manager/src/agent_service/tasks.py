from agent_service.service import AgentService

def run_container_task(container_data: dict):
    agent_service = AgentService()
    return agent_service.run_container(container_data)


def stop_container_task(container_name: str):
    agent_service = AgentService()
    return agent_service.stop_container(container_name)

def delete_container_task(container_name: str):
    agent_service = AgentService()
    return agent_service.delete_container(container_name)

def list_containers_task(prefix: str = None):
    agent_service = AgentService()
    return agent_service.list_containers(prefix)


def create_network_task(network_data: dict):
    agent_service = AgentService()
    return agent_service.create_network(network_data)


def delete_network_task(network_name: str):
    agent_service = AgentService()
    return agent_service.delete_network(network_name)


def attach_network_task(network_data: dict):
    agent_service = AgentService()
    return agent_service.attach_network(network_data)
