from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

EVENTS_PROCESSED = Counter("events_processed_total", "Events successfully processed", ["source", "event_type"])
EVENTS_FAILED = Counter("events_failed_total", "Events which failed processing", ["source", "event_type"])
DUPLICATE_EVENTS = Counter("duplicate_events_total", "Duplicate event deliveries", ["source"])
EVENT_PROCESSING_DURATION = Histogram("event_processing_duration_seconds", "End-to-end event processing duration", ["event_type"])
TWIN_UPDATE_DURATION = Histogram("twin_update_duration_seconds", "Digital twin update duration", ["event_type"])
CONTEXT_BUILD_DURATION = Histogram("context_build_duration_seconds", "Context construction duration", ["event_type"])
ACTION_GENERATION_DURATION = Histogram("action_generation_duration_seconds", "Action generation duration", ["event_type"])
OUTBOX_PENDING = Gauge("outbox_pending_total", "Outbox messages awaiting delivery")
OUTBOX_FAILED = Gauge("outbox_failed_total", "Outbox messages dead-lettered")
VERSION_CONFLICTS = Counter("version_conflicts_total", "Optimistic concurrency conflicts", ["model"])
REPLAY_DURATION = Histogram("replay_duration_seconds", "Replay duration", ["plant_id"])
RULE_EXECUTIONS = Counter("rule_executions_total", "Rule executions", ["rule", "outcome"])
