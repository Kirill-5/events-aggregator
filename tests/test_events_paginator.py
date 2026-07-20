import pytest
from unittest.mock import AsyncMock
from app.services.events_paginator import EventsPaginator


@pytest.mark.asyncio
async def test_events_paginator_multiple_pages():
    mock_client = AsyncMock()
    mock_client.events.side_effect = [
        {"results": [{"id": 1}, {"id": 2}], "next": "cursor2"},
        {"results": [{"id": 3}], "next": None}
    ]

    paginator = EventsPaginator(mock_client)
    events = []
    async for event in paginator:
        events.append(event)

    assert len(events) == 3
    assert events[0]["id"] == 1
    assert events[1]["id"] == 2
    assert events[2]["id"] == 3


@pytest.mark.asyncio
async def test_events_paginator_empty_first_page():
    mock_client = AsyncMock()
    mock_client.events.side_effect = [
        {"results": [], "next": "cursor2"},
        {"results": [{"id": 1}], "next": None}
    ]

    paginator = EventsPaginator(mock_client)
    events = []
    async for event in paginator:
        events.append(event)

    assert len(events) == 1
    assert events[0]["id"] == 1


@pytest.mark.asyncio
async def test_events_paginator_no_events():
    mock_client = AsyncMock()
    mock_client.events.return_value = {"results": [], "next": None}

    paginator = EventsPaginator(mock_client)
    events = []
    async for event in paginator:
        events.append(event)

    assert len(events) == 0