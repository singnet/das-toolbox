from agent_service.tasks import list_containers_task

class ListCommand:
    def __init__(self, subparsers):
        self.parser = subparsers.add_parser("list", help="List workers")
        self.parser.add_argument("--repository", required=True, help="Workspace name")
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        prefix = f"{args.repository}-github-runner"

        containers = list_containers_task(prefix=prefix)

        if not containers:
            print(f"No containers are up for repository: {args.repository}")
        else:
            print(f"Containers for repository: {args.repository}")
            for container in containers:
                print(f"ID: {container['id']}, Name: {container['name']}, Status: {container['status']}")
