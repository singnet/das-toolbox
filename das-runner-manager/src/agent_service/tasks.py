from agent_service.service import AgentService

def start_container_task(container_data: dict):
    agent_service = AgentService()
    return agent_service.start_container(container_data)

def stop_container_task(container_name: str):
    agent_service = AgentService()
    return agent_service.stop_container(container_name)

def delete_container_task(container_name: str):
    agent_service = AgentService()
    return agent_service.delete_container(container_name)

def list_containers_task(prefix: str = None):
    agent_service = AgentService()
    return agent_service.list_containers(prefix)
