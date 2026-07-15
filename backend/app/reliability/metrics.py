from __future__ import annotations

from contextlib import nullcontext

try:
	from prometheus_client import Counter, Gauge, Histogram
except ModuleNotFoundError:  # pragma: no cover - fallback for constrained local environments
	class _NoOpMetric:
		def __init__(self, *args, **kwargs):
			self._labels = {}

		def labels(self, **kwargs):
			key = tuple(sorted(kwargs.items()))
			metric = self._labels.get(key)
			if metric is None:
				metric = self.__class__()
				self._labels[key] = metric
			return metric

		def inc(self, amount: float = 1.0) -> None:
			return None

		def set(self, value: float) -> None:
			return None

		def time(self):
			return nullcontext()

	class Counter(_NoOpMetric):
		pass

	class Gauge(_NoOpMetric):
		pass

	class Histogram(_NoOpMetric):
		pass

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
GRAPH_NODES = Gauge("graph_nodes_total", "Current graph nodes", ["node_type"])
GRAPH_RELATIONSHIPS = Gauge("graph_relationships_total", "Current graph relationships", ["relationship_type"])
GRAPH_UPDATES = Counter("graph_updates_total", "Graph synchronization updates", ["result"])
GRAPH_SYNC_SUCCESS = Counter("graph_sync_success_total", "Successful graph synchronizations")
GRAPH_SYNC_FAILURE = Counter("graph_sync_failure_total", "Failed graph synchronizations")
GRAPH_SYNC_DURATION = Histogram("graph_sync_duration_seconds", "Graph synchronization duration")
GRAPH_QUERY_DURATION = Histogram("graph_query_duration_seconds", "Graph query duration", ["query"])
GRAPH_REBUILD_DURATION = Histogram("graph_rebuild_duration_seconds", "Graph rebuild duration", ["mode"])
GRAPH_REPLAY_DURATION = Histogram("graph_replay_duration_seconds", "Replay graph synchronization duration")
GRAPH_REVISION_LAG = Gauge("graph_revision_lag", "Twin to graph revision lag", ["plant_id"])
GRAPH_FAILED_RECOVERIES = Counter("graph_failed_recoveries_total", "Failed graph recoveries")
GRAPH_TEMPORAL_RELATIONSHIPS = Counter("graph_temporal_relationships_total", "Temporal relationship versions", ["relationship_type"])
RISK_ASSESSMENTS = Counter("risk_assessments_total", "Persisted risk assessments", ["level"])
RISK_RULE_MATCHES = Counter("risk_rule_matches_total", "Matched deterministic risk rules", ["rule_id"])
RISK_ENGINE_LATENCY = Histogram("risk_engine_latency_seconds", "Risk assessment duration")
RISK_ENGINE_DURATION = Histogram("risk_engine_duration_seconds", "Risk engine end-to-end duration")
RISK_RULE_DURATION = Histogram("risk_rule_duration_seconds", "Risk rule evaluation duration", ["rule_id"])
RISK_LEVEL = Gauge("risk_level_total", "Current risk assessment count by level", ["level"])
CRITICAL_RISKS = Gauge("critical_risk_total", "Current critical risks")
ACTIVE_RISKS = Gauge("active_risks_total", "Current active risks")
AGGREGATION_DURATION = Histogram("aggregation_duration_seconds", "Risk aggregation duration")
TIMELINE_LATENCY = Histogram("timeline_latency_seconds", "Risk timeline query duration")
HEATMAP_REQUESTS = Counter("heatmap_requests_total", "Risk map projection requests")
RISK_TIMELINE_QUERIES = Counter("timeline_queries_total", "Risk timeline and history requests")
RISK_DISTRIBUTION = Counter("risk_distribution_total", "Risk assessments by distribution bucket", ["level"])
ACTIONS_GENERATED = Counter("actions_generated_total", "Generated actions from risk assessments")
RECOMMENDATIONS_GENERATED = Counter("recommendations_generated_total", "Generated deterministic recommendations")
RETRIEVAL_LATENCY = Histogram("retrieval_latency_seconds", "Document retrieval latency")
EMBEDDING_LATENCY = Histogram("embedding_latency_seconds", "Document embedding latency")
SEARCH_LATENCY = Histogram("search_latency_seconds", "Hybrid search latency")
VECTOR_QUERIES = Counter("vector_queries_total", "Vector search queries")
AGENT_EXECUTION_TIME = Histogram("agent_execution_time_seconds", "Agent execution latency", ["agent"])
DOCUMENT_INGESTION = Counter("document_ingestion_total", "Document ingestion events", ["source_type"])
CITATION_GENERATION = Counter("citation_generation_total", "Generated citations")
RAG_CONFIDENCE = Gauge("rag_confidence", "Current RAG confidence score")
