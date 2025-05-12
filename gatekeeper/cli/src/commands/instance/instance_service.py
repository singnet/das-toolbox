import httpx
from common.api_client import APIClient
from common.utils import get_hardware_fingerprint, get_machine_info
from common.exceptions import InvalidRequestError, InstanceAlreadyJoinedError


class InstanceService:
    def __init__(self, api_client: APIClient):
        self._api_client = api_client

    def join(self) -> dict:
        instance_id = get_hardware_fingerprint()
        machine_info = get_machine_info()
        payload = {
            "instance_id": instance_id,
            "name": machine_info['hostname'],
            "meta": machine_info,
        }

        try:
            return self._api_client.create("api/instances", payload)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            resp = e.response.json()
            if status == 400:
                raise InvalidRequestError(resp, payload) from e
            elif status == 409:
                raise InstanceAlreadyJoinedError(resp, payload) from e
            raise
