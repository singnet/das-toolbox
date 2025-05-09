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

    async def create(
        self,
        endpoint: str,
        data: dict,
    ) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/{endpoint}", json=data)
            response.raise_for_status()
            return response.json()

    async def read(
        self,
        endpoint: str,
        params: Optional[dict] = None,
    ) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()

    async def update(
        self,
        endpoint: str,
        data: dict,
    ) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(f"{self.base_url}/{endpoint}", json=data)
            response.raise_for_status()
            return response.json()

    async def delete(self, endpoint: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(f"{self.base_url}/{endpoint}")
            response.raise_for_status()
            return response.json()
