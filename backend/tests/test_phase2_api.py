from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_event_triggers_phase2_flow(client, mock_publisher) -> None:
    response = await client.post(
        "/events",
        json={
            "source": "badge-reader",
            "event_type": "ENTRY",
            "plant_id": "plant-a",
            "zone_id": "restricted_area",
            "worker_id": "worker-1",
            "severity": "WARNING",
            "payload": {},
            "metadata": {},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["event_type"] == "ENTRY"

    context_response = await client.get("/contexts/latest")
    assert context_response.status_code == 200
    assert context_response.json()["context_id"] != ""

    action_response = await client.get("/actions/latest")
    assert action_response.status_code == 200
    assert action_response.json()["action_type"] == "RESTRICTED_ZONE_ENTRY"

    plant_state = await client.get("/twin/plants/plant-a")
    assert plant_state.status_code == 200
    assert plant_state.json()["plant_id"] == "plant-a"

    assert any(event.get("event_name") == "ContextBuilt" for event in mock_publisher.published_events)
    assert any(event.get("event_name") == "ActionGenerated" for event in mock_publisher.published_events)
