import httpx
from .config import BASE_URL
from .exceptions import APIClientException

class APIClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url)

    def get(self, endpoint: str, params: dict = None):
        try:
            response = self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise APIClientException(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            raise APIClientException(f"An error occurred while requesting: {e}")

    def post(self, endpoint: str, json_data: dict):
        try:
            response = self.client.post(endpoint, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise APIClientException(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            raise APIClientException(f"An error occurred while requesting: {e}")

    def delete(self, endpoint: str):
        try:
            response = self.client.delete(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise APIClientException(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            raise APIClientException(f"An error occurred while requesting: {e}")
