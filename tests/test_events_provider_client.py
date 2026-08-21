import pytest
from unittest.mock import Mock, patch
from app.services.events_provider_client import EventsProviderClient


@pytest.mark.asyncio
async def test_events():
    mock_response = Mock()
    mock_response.json = Mock(return_value={"results": [{"id": 1}], "next": None})

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        client = EventsProviderClient("http://test.com", "api_key")
        result = await client.events(cursor="cursor1", changed_at="2000-01-01")

        mock_get.assert_called_once_with(
            "http://test.com/api/events/",
            params={"cursor": "cursor1", "changed_at": "2000-01-01"},
            headers={"x-api-key": "api_key"},
        )
        assert result == {"results": [{"id": 1}], "next": None}


@pytest.mark.asyncio
async def test_events_with_cursor():
    mock_response = Mock()
    mock_response.json = Mock(return_value={"results": [{"id": 1}], "next": "next_url"})

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        client = EventsProviderClient("http://test.com", "api_key")
        result = await client.events(cursor="cursor_url", changed_at="2000-01-01")

        mock_get.assert_called_once_with("cursor_url", headers={"x-api-key": "api_key"})
        assert result == {"results": [{"id": 1}], "next": "next_url"}


@pytest.mark.asyncio
async def test_cancel():
    mock_response = Mock()
    mock_response.json = Mock(return_value={"success": True})

    with patch("httpx.AsyncClient.request", return_value=mock_response) as mock_request:
        client = EventsProviderClient("http://test.com", "api_key")
        result = await client.cancel("event123", "ticket456")

        mock_request.assert_called_once_with(
            method="DELETE",
            url="http://test.com/api/events/event123/unregister/",
            json={"ticket_id": "ticket456"},
            headers={"x-api-key": "api_key", "Content-Type": "application/json"},
        )
        assert result == {"success": True}


@pytest.mark.asyncio
async def test_seats():
    mock_response = Mock()
    mock_response.json = Mock(return_value={"seats": ["A1", "A2"]})

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        client = EventsProviderClient("http://test.com", "api_key")
        result = await client.seats("event123")

        mock_get.assert_called_once_with(
            "http://test.com/api/events/event123/seats/",
            headers={"x-api-key": "api_key"},
        )
        assert result == {"seats": ["A1", "A2"]}
