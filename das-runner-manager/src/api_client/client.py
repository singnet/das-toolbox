import httpx
from .config import BASE_URL, TIMEOUT
from .exceptions import APIClientException

class APIClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url, timeout=TIMEOUT)

    def get(self, endpoint: str, params: dict = None):
        response = self.client.get(endpoint, params=params)
        if response.status_code > 400:
            raise APIClientException(f"API request failed with status code {response.status_code}: {response.text}")
        return response.json()

    def post(self, endpoint: str, json_data: dict):
        response = self.client.post(endpoint, json=json_data)

        if response.status_code > 400:
            raise APIClientException(f"API request failed with status code {response.status_code}: {response.text}")

        return response.json()

    def delete(self, endpoint: str):
        response = self.client.delete(endpoint)
        if response.status_code > 400:
            raise APIClientException(f"API request failed with status code {response.status_code}: {response.text}")
        return response.json()