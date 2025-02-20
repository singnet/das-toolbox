import docker
from agent_service.tasks import delete_network_task


class StopAgentCommand:
    def __init__(self, subparsers):
        self.client = docker.from_env()
        self.parser = subparsers.add_parser(
            "stop-agent", help="Stops the agent container"
        )
        self.parser.set_defaults(func=self.run)

    # def _delete_network(self, network_name: str):
    #     try:
    #         result = delete_network_task(network_name)
    #         print(f"Network deletion result: {result}")
    #     except Exception as e:
    #         error_message = str(e).lower()
    #         if "not found" in error_message:
    #             print(f"Network '{network_name}' not found. Continuing...")
    #         else:
    #             raise

    def run(self, args):
        try:
            # self._delete_network("das-runner-network")
            container = self.client.containers.get("das-runner-manager-agent")
            container.stop()
            container.remove()
            print("The agent has been successfully stopped!")
        except docker.errors.NotFound:
            print("Agent container not found.")
        except Exception as e:
            print(f"Failed to stop the agent: {e}")
