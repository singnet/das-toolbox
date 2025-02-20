import docker
from agent_service.tasks import create_network_task, attach_network_task


class StartAgentCommand:
    def __init__(self, subparsers):
        self.client = docker.from_env()
        self.parser = subparsers.add_parser(
            "start-agent", help="Starts the agent container"
        )
        self.parser.set_defaults(func=self.run)

    # def _create_network(self, network_data: dict):
    #     try:
    #         result = create_network_task(network_data)
    #         print(f"Network creation result: {result}")
    #     except Exception as e:
    #         error_message = str(e).lower()
    #         if "already exists" in error_message:
    #             print(
    #                 f"Network '{network_data['network_name']}' already exists. Continuing..."
    #             )
    #         else:
    #             raise

    # def _attach_network(self, network_data: dict):
    #     try:
    #         attach_result = attach_network_task(network_data)
    #         print(f"Network attachment result: {attach_result}")
    #     except Exception as e:
    #         print(f"Failed to attach the container to the network: {e}")

    def run(self, args):
        try:
            container = self.client.containers.run(
                image="levisingnet/das-runner-manager-agent:latest",
                name="das-runner-manager-agent",
                volumes={
                    "/var/run/docker.sock": {
                        "bind": "/var/run/docker.sock",
                        "mode": "rw",
                    }
                },
                network_mode="host",
                detach=True,
            )
            print(
                f"The agent has been successfully started and is running in the container with ID {container.id}!"
            )
        except Exception as e:
            print(f"Failed to start the agent: {e}")
