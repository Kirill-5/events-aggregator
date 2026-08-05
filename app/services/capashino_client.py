from urllib.parse import urljoin
import httpx
from typing import Dict, Any


class CapashinoClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)



async def send_notification(self, message: str, reference_id: str, idempotency_key: str) -> Dict[str, Any]:
    url = urljoin(self.base_url + "/", "api/notifications")
    headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
    data = {
        "message": message,
        "reference_id": reference_id,
        "idempotency_key": idempotency_key
    }
    response = await self.client.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()











