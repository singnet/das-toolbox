import httpx
from typing import Optional


class APIClient:
    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
    ):
        self.base_url = base_url
        self.timeout = timeout

    def create(
        self,
        endpoint: str,
        data: dict = {},
    ) -> dict:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/{endpoint}", json=data)
            response.raise_for_status()
            return response.json()

    def read(
        self,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()

    def update(
        self,
        endpoint: str,
        data: dict,
    ) -> dict:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.put(f"{self.base_url}/{endpoint}", json=data)
            response.raise_for_status()
            return response.json()

    def delete(self, endpoint: str) -> dict:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.delete(f"{self.base_url}/{endpoint}")
            response.raise_for_status()
            return response.json()
