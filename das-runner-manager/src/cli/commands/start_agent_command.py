import docker
import time
from agent_service.tasks import create_network_task, attach_network_task


class StartAgentCommand:
    def __init__(self, subparsers):
        self.client = docker.from_env()
        self.parser = subparsers.add_parser(
            "start-agent", help="Starts the agent container"
        )
        self.parser.set_defaults(func=self.run)

    def _create_network(self, network_data: dict):
        try:
            result = create_network_task(network_data)
            print(f"Network creation result: {result}")
        except Exception as e:
            error_message = str(e).lower()
            if "already exists" in error_message:
                print(
                    f"Network '{network_data['network_name']}' already exists. Continuing..."
                )
            else:
                raise

    def _attach_network(self, network_data: dict):
        try:
            attach_result = attach_network_task(network_data)
            print(f"Network attachment result: {attach_result}")
        except Exception as e:
            print(f"Failed to attach the container to the network: {e}")

    def _wait_container_healthy(self, container):
        while True:
            container.reload()
            health_status = container.attrs["State"]["Health"]["Status"]
            print(f"Current health status: {health_status}")

            if health_status == "healthy":
                print("Container is healthy, proceeding with network creation...")
                break
            else:
                print("Waiting for container to be healthy...")
                time.sleep(5)

    def run(self, args):
        try:
            container_name = "das-runner-manager-agent"
            network_name = "das-runner-network"
            agent_port = 3000

            volumes = {
                "/var/run/docker.sock": {
                    "bind": "/var/run/docker.sock",
                    "mode": "rw",
                }
            }

            ports = {
                agent_port: agent_port,
            }

            healthcheck = {
                "test": ["CMD", "curl", "-f", "http://localhost:3000/health"],
                "interval": 10_000_000_000,
                "timeout": 5_000_000_000,
                "retries": 3,
                "start_period": 10_000_000_000,
            }

            restart_policy = {"Name": "always"}

            container = self.client.containers.run(
                image="levisingnet/das-runner-manager-agent:latest",
                name=container_name,
                volumes=volumes,
                ports=ports,
                detach=True,
                healthcheck=healthcheck,
                restart_policy=restart_policy,
            )
            print(
                f"The agent has been successfully started on port 3000 and is running in the container with ID {container.id}!"
            )

            self._wait_container_healthy(container)

            self._create_network({"network_name": network_name})
            self._attach_network(
                {
                    "network_name": network_name,
                    "container_name": container_name,
                }
            )

        except Exception as e:
            if "Conflict" in str(e):
                print(
                    f"The container '{container_name}' is already running. No action needed."
                )
            else:
                print(f"Failed to start the agent: {e}")
