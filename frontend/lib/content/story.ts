/**
 * Static narrative content shaped like backend DTOs.
 * Structured for future API integration without redesign.
 */

export type Severity = "info" | "warning" | "critical";

export interface StoryEvent {
  event_id: string;
  external_event_id: string;
  source: string;
  event_type: string;
  plant_id: string;
  zone_id: string;
  severity: Severity;
  isDuplicate?: boolean;
}

export interface TwinEntity {
  id: string;
  type: "zone" | "equipment" | "worker" | "sensor";
  label: string;
  plant_id: string;
  zone_id: string;
  status: string;
  version: number;
}

export interface ContextSnapshot {
  context_id: string;
  zone: string;
  workers: number;
  equipment_running: number;
  active_permits: string[];
  hazards: string[];
  timestamp: string;
}

export interface RiskAssessment {
  risk_id: string;
  plant_id: string;
  zone_id: string;
  risk_score: number;
  risk_level: "MODERATE" | "HIGH" | "CRITICAL";
  confidence: number;
  explanation: string;
  recommendations: string[];
  evidence: { rule_id: string; description: string; confidence: number }[];
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  x: number;
  y: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface GeoZone {
  id: string;
  label: string;
  risk_level: Severity;
}

export interface Citation {
  id: string;
  source: string;
  excerpt: string;
}

export interface IntelligenceReport {
  risk_id: string;
  summary: string;
  regulations: string[];
  root_causes: string[];
  recommendations: string[];
  citations: Citation[];
}

export interface IncidentState {
  status: string;
  label: string;
}

export interface HealthStatus {
  status: "ok" | "degraded";
  database: boolean;
  kafka: boolean;
  outbox_worker: boolean;
  neo4j: boolean;
  replay_service: boolean;
}

export const CHALLENGE_SIGNALS = [
  { label: "Gas Sensors", icon: "sensor" },
  { label: "Vision Systems", icon: "vision" },
  { label: "Worker Activity", icon: "worker" },
  { label: "Equipment Telemetry", icon: "equipment" },
  { label: "Permits", icon: "permit" },
  { label: "Emergency Incidents", icon: "incident" },
] as const;

export const STORY_EVENTS: StoryEvent[] = [
  {
    event_id: "evt-001",
    external_event_id: "gas-battery-a-4421",
    source: "sensor-gateway",
    event_type: "GAS_SENSOR",
    plant_id: "plant-a",
    zone_id: "Battery_A",
    severity: "warning",
  },
  {
    event_id: "evt-002",
    external_event_id: "permit-hw-1182",
    source: "permit-system",
    event_type: "HOT_WORK",
    plant_id: "plant-a",
    zone_id: "Battery_A",
    severity: "info",
  },
  {
    event_id: "evt-003",
    external_event_id: "vision-track-77",
    source: "vision-cam-04",
    event_type: "PPE_VIOLATION",
    plant_id: "plant-a",
    zone_id: "Battery_A",
    severity: "critical",
  },
  {
    event_id: "evt-004",
    external_event_id: "gas-battery-a-4421",
    source: "sensor-gateway",
    event_type: "GAS_SENSOR",
    plant_id: "plant-a",
    zone_id: "Battery_A",
    severity: "warning",
    isDuplicate: true,
  },
  {
    event_id: "evt-005",
    external_event_id: "entry-gate-3",
    source: "access-control",
    event_type: "ENTRY",
    plant_id: "plant-a",
    zone_id: "Battery_A",
    severity: "info",
  },
  {
    event_id: "evt-006",
    external_event_id: "equip-vib-902",
    source: "plc-monitor",
    event_type: "VIBRATION_SENSOR",
    plant_id: "plant-a",
    zone_id: "Compressor_Bay",
    severity: "warning",
  },
];

export const TWIN_ENTITIES: TwinEntity[] = [
  {
    id: "Battery_A",
    type: "zone",
    label: "Battery A",
    plant_id: "plant-a",
    zone_id: "Battery_A",
    status: "ACTIVE",
    version: 12,
  },
  {
    id: "eq-compressor-01",
    type: "equipment",
    label: "Compressor 01",
    plant_id: "plant-a",
    zone_id: "Compressor_Bay",
    status: "RUNNING",
    version: 8,
  },
  {
    id: "wkr-4421",
    type: "worker",
    label: "Worker #4421",
    plant_id: "plant-a",
    zone_id: "Battery_A",
    status: "ON_SITE",
    version: 3,
  },
  {
    id: "sns-gas-07",
    type: "sensor",
    label: "Gas Sensor 07",
    plant_id: "plant-a",
    zone_id: "Battery_A",
    status: "ALERT",
    version: 15,
  },
];

export const CONTEXT_SNAPSHOT: ContextSnapshot = {
  context_id: "ctx-8f2a91",
  zone: "Battery_A",
  workers: 3,
  equipment_running: 2,
  active_permits: ["HOT_WORK", "CONFINED_SPACE"],
  hazards: ["Elevated gas ppm", "PPE non-compliance"],
  timestamp: "2026-07-16T14:32:00Z",
};

export const RISK_ASSESSMENT: RiskAssessment = {
  risk_id: "risk-7c4e21",
  plant_id: "plant-a",
  zone_id: "Battery_A",
  risk_score: 87,
  risk_level: "CRITICAL",
  confidence: 0.92,
  explanation:
    "Hot work permit active while gas sensor readings exceed threshold. Worker density in adjacent zone increases exposure.",
  recommendations: [
    "Suspend hot work permit immediately",
    "Dispatch inspection to Battery A",
    "Notify zone supervisor",
    "Expand exclusion perimeter by 30m",
  ],
  evidence: [
    {
      rule_id: "hot_work_plus_gas",
      description: "Hot work + elevated gas detected in same operational window",
      confidence: 0.94,
    },
    {
      rule_id: "worker_density",
      description: "Worker count exceeds safe density threshold for zone",
      confidence: 0.88,
    },
    {
      rule_id: "permit_overlap",
      description: "Confined space permit overlaps hot work boundary",
      confidence: 0.81,
    },
  ],
};

export const GRAPH_NODES: GraphNode[] = [
  { id: "plant-a", type: "Plant", label: "Plant A", x: 120, y: 40 },
  { id: "Battery_A", type: "Zone", label: "Battery A", x: 120, y: 100 },
  { id: "eq-compressor-01", type: "Equipment", label: "Compressor 01", x: 60, y: 160 },
  { id: "wkr-4421", type: "Worker", label: "Worker #4421", x: 180, y: 160 },
  { id: "sns-gas-07", type: "Sensor", label: "Gas Sensor 07", x: 120, y: 200 },
  { id: "hz-gas-cloud", type: "Hazard", label: "Gas Cloud", x: 200, y: 120 },
];

export const GRAPH_EDGES: GraphEdge[] = [
  { source: "plant-a", target: "Battery_A", type: "CONTAINS" },
  { source: "Battery_A", target: "eq-compressor-01", type: "CONTAINS" },
  { source: "Battery_A", target: "wkr-4421", type: "LOCATED_IN" },
  { source: "sns-gas-07", target: "Battery_A", type: "MONITORS" },
  { source: "hz-gas-cloud", target: "Battery_A", type: "THREATENS" },
  { source: "eq-compressor-01", target: "sns-gas-07", type: "DEPENDS_ON" },
];

export const GEO_ZONES: GeoZone[] = [
  { id: "Battery_A", label: "Battery A", risk_level: "critical" },
  { id: "Compressor_Bay", label: "Compressor Bay", risk_level: "warning" },
  { id: "Assembly_North", label: "Assembly North", risk_level: "info" },
];

export const INTELLIGENCE_REPORT: IntelligenceReport = {
  risk_id: "risk-7c4e21",
  summary:
    "Simultaneous hot work and elevated gas readings require immediate permit suspension per OISD-STD-118 guidelines.",
  regulations: [
    "OISD-STD-118: Hot work prohibited when gas readings exceed 10% LEL",
    "Factory Act §41: Adequate ventilation required in confined operations",
  ],
  root_causes: [
    "Permit overlap between hot work and confined space operations",
    "Gas sensor threshold breach not triggering automatic permit hold",
  ],
  recommendations: [
    "Suspend HOT_WORK permit #1182",
    "Establish 30m exclusion zone",
    "Deploy additional gas monitoring",
  ],
  citations: [
    {
      id: "cite-01",
      source: "OISD Hot Work Guidance",
      excerpt: "Hot work shall cease when LEL exceeds 10% in adjacent zones.",
    },
    {
      id: "cite-02",
      source: "Incident Report IR-2024-0891",
      excerpt: "Similar incident resulted from permit overlap in Battery section.",
    },
    {
      id: "cite-03",
      source: "DGMS Confined Space Controls",
      excerpt: "Entry permits must not overlap with active hot work boundaries.",
    },
  ],
};

export const INCIDENT_LIFECYCLE: IncidentState[] = [
  { status: "DETECTED", label: "Detected" },
  { status: "VALIDATED", label: "Validated" },
  { status: "DECLARED", label: "Declared" },
  { status: "RESPONSE_STARTED", label: "Response" },
  { status: "CONTAINMENT", label: "Containment" },
  { status: "RESOLVED", label: "Resolved" },
];

export const HEALTH_STATUS: HealthStatus = {
  status: "ok",
  database: true,
  kafka: true,
  outbox_worker: true,
  neo4j: true,
  replay_service: true,
};

export const RELIABILITY_CONCEPTS = [
  {
    label: "Idempotent ingestion",
    detail: "processed_events ledger prevents duplicate projections",
  },
  {
    label: "Transactional outbox",
    detail: "Atomic publish with exponential backoff and dead-lettering",
  },
  {
    label: "Kafka pipeline",
    detail: "At-least-once delivery to downstream consumers",
  },
  {
    label: "Replay service",
    detail: "Deterministic projection rebuilds from event history",
  },
] as const;
