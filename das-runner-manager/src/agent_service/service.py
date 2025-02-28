from api_client.client import APIClient
from api_client.exceptions import APIClientException
from agent_service.utils import log_agent_activity

class AgentService:
    def __init__(self):
        self.client = APIClient()

    def attach_network(self, network_data: dict):
        try:
            network_name = network_data.get("network_name")
            container_name = network_data.get("container_name")

            if not network_name or not container_name:
                raise ValueError(
                    "Both 'network_name' and 'container_name' must be provided"
                )

            response = self.client.post(
                f"/networks/{network_name}/connect",
                json_data={"container_name": container_name},
            )
            log_agent_activity(
                f"Container '{container_name}' attached to network '{network_name}' successfully."
            )
            return response
        except APIClientException as e:
            log_agent_activity(
                f"Error attaching container '{container_name}' to network '{network_name}': {e}"
            )
            raise

    def create_network(self, network_data: dict):
        try:
            response = self.client.post("/networks", json_data=network_data)
            log_agent_activity(f"Network created {response['network_id']}")
            return response
        except APIClientException as e:
            log_agent_activity(f"Error creating network: {e}")
            raise

    def delete_network(self, network_name: str):
        try:
            response = self.client.delete(f"/networks/{network_name}")
            log_agent_activity(f"Network '{network_name}' deleted successfully.")
            return response
        except APIClientException as e:
            log_agent_activity(f"Error deleting network '{network_name}': {e}")
            raise

    def run_container(self, container_data: dict):
        try:
            response = self.client.post("/containers/run", json_data=container_data)
            log_agent_activity(f"Started container {response['container_id']}")
            return response
        except APIClientException as e:
            log_agent_activity(f"Error starting container: {e}")
            raise

    def stop_container(self, container_name: str):
        try:
            response = self.client.post(f"/containers/{container_name}/stop", json_data={})
            log_agent_activity(f"Stopped container {container_name}")
            return response
        except APIClientException as e:
            log_agent_activity(f"Error stopping container: {e}")
            raise

    def delete_container(self, container_name: str):
        try:
            response = self.client.delete(f"/containers/{container_name}")
            log_agent_activity(f"Deleted container {container_name}")
            return response
        except APIClientException as e:
            log_agent_activity(f"Error deleting container {container_name}: {e}")
            raise

    def list_containers(self, prefix: str = None):
        try:
            response = self.client.get("/containers")
            containers = response.get("containers", [])

            container_status = []
            for container in containers:
                if prefix and not container['name'].startswith(prefix):
                    continue

                container_info = {
                    'id': container['id'],
                    'name': container['name'],
                    'status': container['status'],
                }
                container_status.append(container_info)

            log_agent_activity(f"Listed containers with prefix {prefix}")
            return container_status
        except APIClientException as e:
            log_agent_activity(f"Error listing containers: {e}")
            raise
