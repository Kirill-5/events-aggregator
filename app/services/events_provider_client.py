from http import client

import httpx
from typing import Optional, List, Dict, Any

class EventsProviderClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)


    async def events(self, cursor: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/events"
        params = {}
        if cursor:
            params["cursor"] = cursor
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


    async def event_detail(self, event_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/events/{event_id}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()


    async def seats(self, event_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/events/{event_id}/seats"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def register(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/tickets"
        response = await self.client.post(url , json={
            "event_id": event_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat
        })
        response.raise_for_status()
        return response.json()


    async def cancel(self, ticket_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/tickets/{ticket_id}"
        response = await self.client.delete(url)
        response.raise_for_status()
        return response.json()

