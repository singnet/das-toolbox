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
                    "labels": container.labels,
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
    network_mode: Union[str, None] = None,
    network: Union[str, None] = None,
    tmpfs: Union[str, None] = None,
    hostname: Union[str, None] = None,
    restart_policy: Union[Dict[str, str], None] = None,
    labels: Union[Dict[str, str], None] = None,
):
    create_kwargs = {
        "image": image,
        "name": name,
        "volumes": volumes,
        "environment": environment,
        "privileged": privileged,
        "tmpfs": tmpfs,
        "hostname": hostname,
        "restart_policy": restart_policy,
        "labels": {k: str(v) for k, v in (labels or {}).items()},
        "detach": detach,
    }

    if network is not None:
        create_kwargs["network"] = network
    else:
        create_kwargs["network_mode"] = network_mode

    try:
        container = client.containers.run(**create_kwargs)

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


def recreate_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        attrs = container.attrs
        name = container.name or container_id

        config = attrs["Config"]
        host_config = attrs["HostConfig"]
        network_settings = attrs.get("NetworkSettings", {})

        image = config["Image"]
        env = {e.split("=", 1)[0]: e.split("=", 1)[1] for e in config.get("Env", [])}
        labels = config.get("Labels", {})
        privileged = host_config.get("Privileged", False)
        restart_policy = host_config.get("RestartPolicy", {})
        tmpfs = host_config.get("Tmpfs", None)

        volumes = {}
        if host_config.get("Binds"):
            for bind in host_config["Binds"]:
                src, dst, mode = bind.split(":")
                volumes[src] = {"bind": dst, "mode": mode}

        network_mode = host_config.get("NetworkMode", None)
        network = None
        if "Networks" in network_settings and len(network_settings["Networks"]) == 1:
            network = list(network_settings["Networks"].keys())[0]

        delete_container(container_id)

        return run_container(
            image=image,
            name=name,
            volumes=volumes,
            environment=env,
            privileged=privileged,
            detach=True,
            network_mode=network_mode,
            network=network,
            tmpfs=tmpfs,
            restart_policy=restart_policy,
            labels=labels,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
