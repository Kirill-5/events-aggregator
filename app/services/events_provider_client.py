import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx

from app.core.metrics import (
    events_provider_request_duration_seconds,
    events_provider_requests_total,
)


class EventsProviderClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=120.0)

    async def _tracked_request(
        self, endpoint_label: str, method: str, url: str, **kwargs
    ) -> httpx.Response:
        start_time = time.monotonic()
        try:
            response = await self.client.request(method, url, **kwargs)
            status = response.status_code
            return response
        except Exception:
            status = "error"
            raise
        finally:
            duration = time.monotonic() - start_time
            events_provider_requests_total.labels(
                endpoint=endpoint_label, status=status
            ).inc()
            events_provider_request_duration_seconds.labels(
                endpoint=endpoint_label
            ).observe(duration)

    async def events(
        self, cursor: Optional[str] = None, changed_at: Optional[str] = None
    ) -> Dict[str, Any]:
        headers = {"x-api-key": self.api_key}

        if cursor:
            response = await self._tracked_request(
                "/events", "GET", cursor, headers=headers
            )
        else:
            url = urljoin(self.base_url + "/", "api/events/")
            params = {}
            if changed_at:
                params["changed_at"] = changed_at
            response = await self._tracked_request(
                "/events", "GET", url, params=params, headers=headers
            )

        response.raise_for_status()
        return response.json()

    async def event_detail(self, event_id: str) -> Dict[str, Any]:
        url = urljoin(self.base_url + "/", f"api/events/{event_id}/")
        headers = {"x-api-key": self.api_key}
        response = await self._tracked_request("/events", "GET", url, headers=headers)
        response.raise_for_status()
        return response.json()

    async def seats(self, event_id: str) -> Dict[str, Any]:
        url = urljoin(self.base_url + "/", f"api/events/{event_id}/seats/")
        headers = {"x-api-key": self.api_key}
        response = await self._tracked_request("/seats", "GET", url, headers=headers)
        response.raise_for_status()
        return response.json()

    async def register(
        self, event_id: str, first_name: str, last_name: str, email: str, seat: str
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url + "/", f"api/events/{event_id}/register/")
        headers = {"x-api-key": self.api_key}
        response = await self._tracked_request(
            "/registration",
            "POST",
            url,
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "seat": seat,
            },
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def cancel(self, event_id: str, ticket_id: str) -> Dict[str, Any]:
        url = urljoin(self.base_url + "/", f"api/events/{event_id}/unregister/")
        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
        response = await self._tracked_request(
            "/registration",
            "DELETE",
            url,
            json={"ticket_id": ticket_id},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
