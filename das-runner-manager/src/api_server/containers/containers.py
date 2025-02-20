from fastapi import HTTPException
from docker import from_env
from typing import Union, Dict

client = from_env()

def list_containers():
    try:
        containers = client.containers.list(all=True)
        return {
            "containers": [
                {
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "image": (
                        container.image.tags[0] if container.image.tags else "unknown"
                    ),
                    "ports": container.ports,
                }
                for container in containers
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_container(
    image: str,
    name: str,
    volumes: dict,
    environment: dict,
    privileged: bool,
    detach: bool,
    network_mode: Union[str, None],
    network: Union[str, None],
    tmpfs: Union[str, None],
    hostname: Union[str, None],
    restart_policy: Union[Dict[str, str], None],
):
    try:
        container = client.containers.run(
            image=image,
            name=name,
            volumes=volumes,
            environment=environment,
            privileged=privileged,
            detach=detach,
            network_mode=network_mode,
            network=network,
            tmpfs=tmpfs,
            hostname=hostname,
            restart_policy=restart_policy,
        )
        return {"message": "Container started", "container_id": container.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def stop_container(name: str):
    try:
        container = client.containers.get(name)
        container.stop()
        return {"message": f"Container {name} stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def delete_container(name: str):
    try:
        container = client.containers.get(name)
        container.stop()
        container.remove()
        return {"message": f"Container {name} removed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start_container(name: str):
    try:
        container = client.containers.get(name)
        container.start()
        return {"message": f"Container {name} started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def restart_container(name: str):
    try:
        stop_container(name)
        start_container(name=name)

        return {"message": f"Container {name} has been successfully restarted."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
