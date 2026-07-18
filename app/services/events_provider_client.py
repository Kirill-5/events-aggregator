import httpx
from typing import Optional, Dict, Any

class EventsProviderClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def events(self, cursor: Optional[str] = None, changed_at: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/events/"
        params = {}
        if cursor:
            params["cursor"] = cursor
        if changed_at:
            params["changed_at"] = changed_at
        headers = {"x-api-key": self.api_key}
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def event_detail(self, event_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/events/{event_id}/"
        headers = {"x-api-key": self.api_key}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    async def seats(self, event_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/events/{event_id}/seats/"
        headers = {"x-api-key": self.api_key}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"Seats response for event {event_id}: {data}")  # Добавить
        return data

    async def register(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/tickets/"
        headers = {"x-api-key": self.api_key}
        response = await self.client.post(
            url,
            json={
                "event_id": event_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "seat": seat
            },
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def cancel(self, ticket_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/tickets/{ticket_id}/"
        headers = {"x-api-key": self.api_key}
        response = await self.client.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()