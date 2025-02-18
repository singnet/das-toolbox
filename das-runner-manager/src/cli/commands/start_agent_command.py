import docker

class StartAgentCommand:
    def __init__(self, subparsers):
        self.client = docker.from_env()
        self.parser = subparsers.add_parser("start-agent", help="Starts the agent container")
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        try:
            container = self.client.containers.run(
                "levisingnet/runner-manager-agent",
                volumes={"/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}},
                network_mode="host",
                detach=True
            )
            print(f"The agent has been successfully started and is running in the container with ID {container.id}!")
        
        except Exception as e:
            print(f"Failed to start the agent: {e}")
