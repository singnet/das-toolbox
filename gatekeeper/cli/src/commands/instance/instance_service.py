import httpx
from common.api_client import APIClient
from common.utils import get_hardware_fingerprint, get_machine_info
from common.exceptions import InvalidRequestError


class InstanceService:
    def __init__(self, api_client: APIClient):
        self._api_client = api_client

    def join(self) -> dict:
        instance_id = get_hardware_fingerprint()
        machine_info = get_machine_info()
        payload = {
            "instance_id": instance_id,
            "name": machine_info['hostname'],
            "metadata": machine_info,
        }

        try:
            return self._api_client.create("api/instances", payload)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                error_message = e.response.json()
                raise InvalidRequestError(error_message, payload) from e
            raise
