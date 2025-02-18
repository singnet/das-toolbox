from agent_service.tasks import stop_container_task, delete_container_task, list_containers_task

class StopCommand:
    def __init__(self, subparsers):
        self.parser = subparsers.add_parser("stop", help="Stop a runner")
        self.parser.add_argument("--repository", required=True, help="Repository name")
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        prefix = f"{args.repository}-github-runner"
        print(f"Stopping containers for repository: {args.repository}")

        containers = list_containers_task(prefix)

        if not containers:
            print(f"No containers found for repository: {args.repository}")
            return

        for container in containers:
            stop_container_task(container['name'])
            print(f"Stopping container: {container['name']}")

        print(f"Pruning stopped containers for repository: {args.repository}")

        for container in containers:
            if container['status'] == 'exited':
                delete_container_task(container['name'])
                print(f"Removed container: {container['name']}")
