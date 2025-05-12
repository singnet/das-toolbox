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
            status = e.response.status_code
            resp = e.response.json()
            if status == 404:
                raise InstanceNotRegisteredError(instance_id, message="You must register (join) this instance before reserving a port.") from e
            elif status == 400 or status == 409:
                error_message = resp.get('error') or resp
                raise InvalidRequestError(error_message, payload) from e
            raise

    def release(self, port_number: int) -> dict:
        try:
            return self._api_client.create(f"api/ports/{port_number}/release")
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            resp = e.response.json()
            if status == 400 or status == 409:
                error_message = resp.get('error') or resp
                raise InvalidRequestError(error_message) from e
            raise