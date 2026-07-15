from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_create_and_fetch_event(client, valid_gas_event_payload) -> None:
    response = await client.post("/events", json=valid_gas_event_payload)
    assert response.status_code == 201

    created = response.json()
    event_id = created["event_id"]
    assert created["payload"]["ppm"] == 42.5

    fetch_response = await client.get(f"/events/{event_id}")
    assert fetch_response.status_code == 200
    assert fetch_response.json()["event_id"] == event_id


@pytest.mark.asyncio
async def test_list_events(client, valid_gas_event_payload) -> None:
    await client.post("/events", json=valid_gas_event_payload)

    response = await client.get("/events")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


@pytest.mark.asyncio
async def test_health_endpoint(client) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
