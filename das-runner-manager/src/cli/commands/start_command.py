import getpass
import os
from agent_service.tasks import run_container_task
from agent_service.utils import handle_connection_refused
import sys


class StartCommand:
    def __init__(self, subparsers):
        self.parser = subparsers.add_parser(
            "start",
            help="Start a runner",
        )
        self.parser.add_argument(
            "--repository",
            required=True,
            help="Repository name",
        )
        self.parser.add_argument(
            "--token",
            help="GitHub Action runner token (will prompt if not provided)",
        )
        self.parser.add_argument(
            "--runners",
            type=int,
            default=1,
            help="Number of runners (default: 1, between 1 and 15)",
        )
        self.parser.add_argument(
            "--no-cache-runners",
            type=int,
            default=0,
            help="Number of runners that should use cache (default: 0)",
        )
        self.parser.set_defaults(func=self.run)

    @handle_connection_refused
    def run(self, args):
        if args.runners < 1 or args.runners > 15:
            print("Error: The number of runners must be between 1 and 15.")
            sys.exit(1)

        if args.no_cache_runners > args.runners or args.no_cache_runners < 0:
            print("Error: The number of cache runners must be at least 0 and no greater than the total number of runners.")
            sys.exit(1)

        if not args.token:
            args.token = getpass.getpass("Enter GitHub Token: ")

            if not args.token:
                print("Error: GitHub token is required.")
                sys.exit(1)

        for i in range(0, args.runners):
            home_dir = os.path.expanduser("~")
            volume = {}
            labels = {}
            container_name = f"{args.repository}-github-runner-{i}"
            network_name = "das-runner-network"
            tmpfs = {}

            if i < args.no_cache_runners:
                labels = {"self-hosted-nocache": ""}

            else:
                volume = {
                    f"{home_dir}/.cache/docker/{args.repository}/{container_name}": {
                        "bind": f"/home/ubuntu/.cache/{args.repository}",
                        "mode": "rw",
                    },
                    f"{home_dir}/.cache/docker/{args.repository}/shared": {
                        "bind": f"/home/ubuntu/.cache/shared",
                        "mode": "rw",
                    },
                }
                labels = {"self-hosted-withcache": ""}


            env_vars = {
                "REPO_URL": f"https://github.com/singnet/{args.repository}",
                "GH_TOKEN": args.token,
                "USER": "ubuntu",
                "EXTRA_LABELS": ",".join(labels.keys()),
            }
            restart_policy = {"Name": "unless-stopped"}

            container_data = {
                "image": "levisingnet/github-runner:ubuntu-22.04",
                "name": container_name,
                "volumes": volume,
                "detach": True,
                "environment": env_vars,
                "privileged": True,
                "network": network_name,
                "restart_policy": restart_policy,
                "labels": labels,
                "tmpfs": tmpfs,
            }

            run_container_task(container_data)
