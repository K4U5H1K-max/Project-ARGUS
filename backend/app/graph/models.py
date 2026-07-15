from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class GraphNodeType(StrEnum):
    PLANT = "Plant"; ZONE = "Zone"; EQUIPMENT = "Equipment"; WORKER = "Worker"; SENSOR = "Sensor"
    PERMIT = "Permit"; MAINTENANCE = "Maintenance"; HAZARD = "Hazard"; INCIDENT = "Incident"; SHIFT = "Shift"; EMERGENCY_TEAM = "EmergencyTeam"


class GraphRelationshipType(StrEnum):
    LOCATED_IN = "LOCATED_IN"; WORKING_IN = "WORKING_IN"; MONITORS = "MONITORS"; CONNECTED_TO = "CONNECTED_TO"; ASSIGNED_TO = "ASSIGNED_TO"
    VALID_FOR = "VALID_FOR"; DETECTS = "DETECTS"; AFFECTED_BY = "AFFECTED_BY"; PART_OF = "PART_OF"; NEAR = "NEAR"; DEPENDS_ON = "DEPENDS_ON"


@dataclass(frozen=True, slots=True)
class GraphNode:
    node_type: GraphNodeType
    node_id: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GraphRelationship:
    source: GraphNode
    relationship_type: GraphRelationshipType
    target: GraphNode
    properties: dict[str, Any] = field(default_factory=dict)
