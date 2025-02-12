import docker
import os

class DockerClient:
    def __init__(self):
        self.client = docker.from_env()

    def get_containers(self, prefix=None):
        containers = self.client.containers.list(all=True)
        container_status = []
        
        for container in containers:
            if prefix and not container.name.startswith(prefix):
                continue

            container_info = {
                'id': container.id,
                'name': container.name,
                'status': container.status,
                'instance': container,
            }
            container_status.append(container_info)
        
        return container_status

    def start_container(
        self,
        gh_token,
        repository,
        sufix="0",
        container_user="ubuntu",
    ):
        volume = {
            f"{os.path.expanduser('~')}/.cache/docker/{repository}": {
                'bind': f'/home/{container_user}/.cache/{repository}',
                'mode': 'rw'
            },
        }

        env_vars = {
            "REPO_URL": f"https://github.com/singnet/{repository}",
            "GH_TOKEN": gh_token,
            "USER": container_user,
        }

        try:
            container = self.client.containers.run(
                "levisingnet/github-runner:ubuntu-22.04",
                name=f"{repository}-github-runner-{sufix}",
                volumes=volume,
                detach=True,
                environment=env_vars,
                privileged=True,
            )
            print(f"Container '{container.name}' started successfully!")
        except docker.errors.APIError as e:
            print(f"Error starting the container: {e}")

    def stop_containers(self, prefix):
        containers = self.get_containers(prefix)

        if not containers:
            print(f"No running containers to stop for prefix: {prefix}")
            return

        for container in containers:
            try:
                container['instance'].stop()
                print(f"Stopped container: {container['name']} ({container['id']})")
            except docker.errors.APIError as e:
                print(f"Error stopping container {container['name']}: {e}")

    def remove_stopped_containers(self, prefix):
        containers = self.get_containers(prefix)

        if not containers:
            print(f"No containers found with prefix: {prefix}")
            return

        for container in containers:
            if container['status'] in ["exited", "created", "dead"]:
                try:
                    container['instance'].remove()
                    print(f"Removed container: {container['name']} ({container['id']})")
                except docker.errors.APIError as e:
                    print(f"Error removing container {container['name']}: {e}")
            else:
                print(f"Skipping active container: {container['name']} (Status: {container['status']})")

