from fastapi import HTTPException
from docker import from_env, errors

client = from_env()


def get_containers_connected_to_network(network_name: str):
    try:
        all_containers = client.containers.list(all=True)

        connected_containers = []
        for container in all_containers:
            container_networks = container.attrs["NetworkSettings"]["Networks"]
            if network_name in container_networks:
                connected_containers.append(container)

        if not connected_containers:
            print(f"No containers are connected to the network '{network_name}'.")
        return connected_containers

    except errors.APIError as e:
        print(f"Failed to retrieve containers: {str(e)}")
        return []


def delete_network(network_name: str):
    try:
        existing_networks = client.networks.list(names=[network_name])

        if not existing_networks:
            return {"message": f"Network '{network_name}' does not exist"}

        network = existing_networks[0]

        connected_containers = get_containers_connected_to_network(network_name)

        if not connected_containers:
            network.remove()
            return {"message": f"Network '{network_name}' deleted successfully."}

        other_containers = [
            container
            for container in connected_containers
            if container.name != "das-runner-manager-agent"
        ]

        if other_containers:
            return {
                "message": f"Network '{network_name}' cannot be removed because other containers are connected to it."
            }

        for container in connected_containers:
            if container.name == "das-runner-manager-agent":
                network.disconnect(container, force=True)
                print(
                    f"Container '{container.name}' disconnected from network '{network_name}'."
                )
                break

        network.remove()
        return {"message": f"Network '{network_name}' deleted successfully."}

    except errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete network: {str(e)}")

    except errors.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete network: {str(e)}"
        )

def create_network(network_name: str, driver: str = "bridge"):
    try:
        existing_networks = client.networks.list(names=[network_name])
        if existing_networks:
            return {
                "message": f"Network '{network_name}' already exists",
                "network_id": existing_networks[0].id,
            }

        network = client.networks.create(name=network_name, driver=driver)
        return {"message": f"Network '{network_name}' created", "network_id": network.id}

    except errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create network: {str(e)}")

def attach_network(network_name: str, container_name: str):
    try:
        network = client.networks.list(names=[network_name])
        if not network:
            raise HTTPException(status_code=404, detail=f"Network '{network_name}' not found")
        network = network[0]

        container = client.containers.list(all=True, filters={"name": container_name})
        if not container:
            raise HTTPException(status_code=404, detail=f"Container '{container_name}' not found")
        container = container[0]

        network.connect(container)
        return {"message": f"Container '{container_name}' attached to network '{network_name}'"}
    
    except errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Failed to attach network: {str(e)}")
