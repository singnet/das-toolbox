from docker_client import DockerClient

class StopCommand:
    def __init__(self, subparsers):
        self.docker_client = DockerClient()

        self.parser = subparsers.add_parser("stop", help="Stop a runner")
        self.parser.add_argument("--repository", required=True, help="Repository name")
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        prefix = f"{args.repository}-github-runner"
        print(f"Stopping containers for repository: {args.repository}")

        self.docker_client.stop_containers(prefix)

        print(f"Pruning stopped containers for repository: {args.repository}")
        self.docker_client.remove_stopped_containers(prefix)
