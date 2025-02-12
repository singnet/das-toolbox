from docker_client import DockerClient
import getpass

class StartCommand:
    def __init__(self, subparsers):
        self.docker_client = DockerClient()

        self.parser = subparsers.add_parser("start", help="Start a runner")
        self.parser.add_argument("--repository", required=True, help="Repository name")
        self.parser.add_argument("--token", help="GitHub Action runner token (will prompt if not provided)")
        self.parser.add_argument("--runners", type=int, required=True, help="Number of runners")
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        if not args.token:
            args.token = getpass.getpass("Enter GitHub Token: ")

            if not args.token:
                print("Error: GitHub token is required.")
                exit(1)

        for i in range(0, args.runners):
            self.docker_client.start_container(
                gh_token=args.token,
                repository=args.repository,
                sufix=i,
            )
