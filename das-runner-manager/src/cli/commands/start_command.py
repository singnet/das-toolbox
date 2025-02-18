import getpass
import os
from agent_service.tasks import start_container_task
import sys

class StartCommand:
    def __init__(self, subparsers):
        self.parser = subparsers.add_parser("start", help="Start a runner")
        self.parser.add_argument("--repository", required=True, help="Repository name")
        self.parser.add_argument("--token", help="GitHub Action runner token (will prompt if not provided)")
        self.parser.add_argument("--runners", type=int, default=1, help="Number of runners (default: 1, between 1 and 15)")
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        if args.runners < 1 or args.runners > 15:
            print("Error: The number of runners must be between 1 and 15.")
            sys.exit(1)

        if not args.token:
            args.token = getpass.getpass("Enter GitHub Token: ")

            if not args.token:
                print("Error: GitHub token is required.")
                sys.exit(1)

        for i in range(0, args.runners):
            volume = {
                f"{os.path.expanduser('~')}/.cache/docker/{args.repository}": {
                    'bind': f'/home/ubuntu/.cache/{args.repository}',
                    'mode': 'rw'
                },
            }

            env_vars = {
                "REPO_URL": f"https://github.com/singnet/{args.repository}",
                "GH_TOKEN": args.token,
                "USER": "ubuntu",
            }

            container_data = {
                "image": "levisingnet/github-runner:ubuntu-22.04",
                "name": f"{args.repository}-github-runner-{i}",
                "volumes": volume,
                "detach": True,
                "environment": env_vars,
                "privileged": True,
            }

            start_container_task(container_data)
