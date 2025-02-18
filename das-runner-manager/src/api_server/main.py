from fastapi import FastAPI
from api_server.containers import containers, models

app = FastAPI()

@app.get("/containers")
def list_containers():
    return containers.list_containers()

@app.post("/containers/start")
def start_container(request: models.DockerContainerRunRequest):
    return containers.start_container(
        image=request.image,
        name=request.name,
        volumes=request.volumes,
        environment=request.environment,
        privileged=request.privileged,
        detach=request.detach
    )

@app.delete("/containers/{name}")
def delete_container(name: str):
    return containers.delete_container(name)

@app.post("/containers/{name}/stop")
def stop_container(name: str):
    return containers.stop_container(name)
