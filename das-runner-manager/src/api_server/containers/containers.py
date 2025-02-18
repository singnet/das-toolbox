from fastapi import HTTPException
from docker import from_env

client = from_env()

def list_containers():
    try:
        containers = client.containers.list(all=True)
        return {"containers": [container.name for container in containers]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_container(image: str, name: str, volumes: dict, environment: dict, privileged: bool, detach: bool):
    try:
        container = client.containers.run(
            image=image,
            name=name,
            volumes=volumes,
            environment=environment,
            privileged=privileged,
            detach=detach
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
