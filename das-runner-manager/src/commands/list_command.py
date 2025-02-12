from docker_client import DockerClient

class ListCommand:
    def __init__(self, subparsers):
        self.docker_client = DockerClient()

        self.parser = subparsers.add_parser("list", help="List workers")
        self.parser.add_argument("--repository", required=True, help="Workspace name")
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        prefix = f"{args.repository}-github-runner"
        containers = self.docker_client.get_containers(prefix)

        if not containers:
            print(f"No containers are up for repository: {args.repository}")
        else:
            print(f"Containers for workspace: {args.repository}")
            for container in containers:
                print(f"ID: {container['id']}, Name: {container['name']}, Status: {container['status']}")

