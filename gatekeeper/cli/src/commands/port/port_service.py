import httpx
from common.api_client import APIClient
from common.utils import get_hardware_fingerprint
from common.exceptions import InstanceNotRegisteredError, InvalidRequestError

class PortService:
    def __init__(self, api_client: APIClient):
        self._api_client = api_client

    def reserve(self) -> dict:
        instance_id = get_hardware_fingerprint()
        payload = {"instance_id": instance_id}

        try:
            return self._api_client.create("api/ports/reserve", payload)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise InstanceNotRegisteredError(instance_id, message="You must register (join) this instance before reserving a port.") from e
            if e.response.status_code == 400:
                error_message = e.response.json()
                raise InvalidRequestError(error_message, payload) from e
            raise

    def release(self, instance_id: str) -> dict:
        payload = {"instance_id": instance_id}
        return self._api_client.create("ports/release", payload)
