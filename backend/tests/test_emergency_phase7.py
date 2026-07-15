import pytest
import uuid
from typing import Dict, Any

from app.emergency.service import EmergencyService
from app.permit.service import PermitIntelligenceService
from app.compliance.service import ComplianceIntelligenceService
from app.notifications.service import NotificationService
from app.actions.service import ActionPlanner
from app.actions.schemas import ActionObject
from app.core.time import utcnow

@pytest.mark.asyncio
async def test_emergency_incident_lifecycle():
    service = EmergencyService()
    risk_id = uuid.uuid4()
    incident = service.create_incident(risk_id, "PLANT_1", "ZONE_A", "HIGH", ["Gas Leak", "Fire"])
    
    assert incident.playbook_id == "PB-GAS-001"
    assert incident.status == "DETECTED"
    
    # Transition
    updated = service.transition_status(incident.incident_id)
    assert updated.status == "VALIDATED"
    
    # Allocate resources
    resources = service.allocate_resources(incident.incident_id)
    assert len(resources) > 0
    assert resources[0].status == "DISPATCHED"

@pytest.mark.asyncio
async def test_permit_conflict_detection():
    service = PermitIntelligenceService()
    active_permits = [
        {"id": "P1", "type": "HOT_WORK"},
        {"id": "P2", "type": "CHEMICAL_WASH"}
    ]
    conflicts = await service.scan_zone_permits("ZONE_A", active_permits)
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == "SIMULTANEOUS_OPERATIONS"

@pytest.mark.asyncio
async def test_compliance_violation():
    service = ComplianceIntelligenceService()
    context_snapshot = {
        "zone": {"plant_id": "PLANT_1", "zone_id": "ZONE_A"},
        "active_permits": [{"id": "P1", "type": "HOT_WORK"}],
        "workers": [{"worker_id": "W1", "ppe": ["Hard Hat", "Safety Glasses"]}]
    }
    violations = await service.scan_context(context_snapshot)
    assert len(violations) == 1
    assert "Gas Mask" in violations[0].description

@pytest.mark.asyncio
async def test_notification_dispatch():
    service = NotificationService()
    event = service.dispatch("EmergencyDeclared", "CRITICAL", {"incident_id": str(uuid.uuid4())})
    assert event.status == "DISPATCHED"
    assert "SMS" in event.channels
    assert "KAFKA" in event.channels
    
    ack = service.acknowledge(event.notification_id, "USER_123")
    assert ack.status == "ACKNOWLEDGED"

@pytest.mark.asyncio
async def test_action_planner():
    planner = ActionPlanner()
    events = [
        ActionObject(action_id=str(uuid.uuid4()), action_type="EVACUATE_ZONE", priority=1, reason="Test", generated_by="Engine", timestamp=utcnow(), context_id=str(uuid.uuid4()), status="EMITTED", action_data={}, plant_id="PLANT", zone_id="ZONE"),
        ActionObject(action_id=str(uuid.uuid4()), action_type="LOCK_EQUIPMENT", priority=2, reason="Test", generated_by="Engine", timestamp=utcnow(), context_id=str(uuid.uuid4()), status="EMITTED", action_data={}, plant_id="PLANT", zone_id="ZONE")
    ]
    plan = planner.generate_plan(events)
    assert plan["status"] == "DRAFT"
    assert len(plan["actions"]) == 2
    assert len(plan["dependencies"]) == 1
