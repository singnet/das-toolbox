from fastapi import HTTPException
from docker import from_env, errors

client = from_env()

def delete_network(network_name: str):
    try:
        existing_networks = client.networks.list(names=[network_name])
        
        if not existing_networks:
            return {"message": f"Network '{network_name}' does not exist"}
        
        network = existing_networks[0]
        network.remove()
        return {"message": f"Network '{network_name}' deleted"}

    except errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete network: {str(e)}")


def create_network(network_name: str, driver: str = "bridge"):
    try:
        existing_networks = client.networks.list(names=[network_name])
        if existing_networks:
            return {"message": f"Network '{network_name}' already exists"}

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