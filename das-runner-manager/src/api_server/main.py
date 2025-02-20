import uvicorn
from fastapi import FastAPI
from api_server.containers import containers, models as container_models
from api_server.networks import networks, models as network_models
from api_server.daemon import docker_daemon

app = FastAPI()


@app.get("/health")
def health_check():
    return docker_daemon.up()


@app.get("/containers")
def list_containers():
    return containers.list_containers()


@app.post("/containers/run")
def run_container(request: container_models.DockerContainerRunRequest):
    return containers.run_container(
        image=request.image,
        name=request.name,
        volumes=request.volumes,
        environment=request.environment,
        privileged=request.privileged,
        detach=request.detach,
        network_mode=request.network_mode,
        network=request.network,
        tmpfs=request.tmpfs,
        hostname=request.hostname,
        restart_policy=request.restart_policy,
    )


@app.delete("/containers/{name}")
def delete_container(name: str):
    return containers.delete_container(name)

@app.post("/containers/{name}/stop")
def stop_container(name: str):
    return containers.stop_container(name)


@app.post("/containers/{name}/restart-sequence")
def restart_container_sequence(name: str):
    return containers.restart_container(name)


@app.post("/networks")
def create_network(request: network_models.NetworkCreateRequest):
    return networks.create_network(
        driver=request.driver,
        network_name=request.network_name,
    )


@app.post("/networks/{network_name}/connect")
def attach_network(network_name: str, request: network_models.AttachNetworkRequest):
    return networks.attach_network(
        network_name=network_name,
        container_name=request.container_name,
    )


@app.delete("/networks/{network_name}")
def delete_network(network_name: str):
    return networks.delete_network(network_name)


if __name__ == "__main__":
    uvicorn.run("api_server.main:app", host="0.0.0.0", port=3000, reload=True)
