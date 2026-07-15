# Project ARGUS Architecture Documentation

Project ARGUS is an AI-powered Industrial Safety Intelligence Platform designed to proactively prevent industrial accidents.

## 1. System Overview

The core architecture operates as follows:
External Events → Event Platform → Digital Twin → Context Engine → Knowledge Graph → Compound Risk Intelligence → Risk Assessment → Geospatial Projection → Action Engine → Transactional Outbox → Kafka

## 2. Industrial Intelligence Layer

The Industrial Intelligence Layer enriches deterministic compound RiskAssessments with RAG-backed insights, finding similar historical incidents, applicable regulations, and root causes without replacing the deterministic safety engine.

### 2.1 RAG Architecture
- **Corpus & Sources**: Ingests OISD Standards, Factory Act, DGMS Guidelines, SOPs, permit procedures, incident reports, and safety bulletins.
- **Pipeline**: Processes files via chunking and metadata extraction. Embeddings are created deterministically and stored for fast vector retrieval.
- **Retrieval**: Uses hybrid search (keyword + semantic) along with metadata filtering and reranking based on risk context (hazards, permits, rules).
- **Citations**: All returned intelligence is strictly backed by document citations to ensure explainability and traceability.

### 2.2 Agent Architecture
Specialized deterministic agents coordinate to analyze safety risks:
- **Incident Intelligence Agent**: Finds and summarizes similar historical incidents and near-misses.
- **Regulation Agent**: Matches regulatory guidelines, SOPs, and required PPE based on risk context.
- **Historical Analysis Agent**: Identifies recurring failures and extracts applicable historical context.
- **Recommendation Agent**: Surfaces preventative actions, maintenance recommendations, and training best practices.
- **Root Cause Agent**: Correlates risk contexts to known root causes to provide deep diagnostic intelligence.

### 2.3 Document Pipeline & Vector Search
- **Ingestion**: Supports PDF, DOCX, TXT, Markdown, and structured JSON.
- **Vector Search**: Embedded vectors are queried using the risk context as the anchor, prioritizing results that match specific plant constraints, overlapping hazards, and active work permits.

### 2.4 Knowledge Fusion
Fuses the Risk Assessment, Knowledge Graph entities, Historical Incidents, Regulations, and Plant Context into a cohesive Industrial Intelligence Report. The report includes risk summaries, historical comparisons, applicable standards, recommendations, and confidence scores with full citation paths.

## 3. Advanced Geospatial Intelligence

The Geospatial Intelligence layer expands the projection service into a comprehensive spatial analytics engine.

### 3.1 Spatial Analytics
- Analyzes true distance, hazard influence radius, and worker exposure radius.
- Detects overlapping hazard zones, risk clusters, and dynamic worker density heatmaps.
- Computes optimal evacuation paths, identifies connected hazardous zones, and locates nearest safe assembly points.

### 3.2 Geospatial APIs
Outputs MapLibre-ready FeatureCollections. Key endpoints include:
- `GET /geo/layout`: Plant blueprints containing zones, buildings, equipment, etc.
- `GET /geo/heatmap`: Dynamic risk intensity heatmaps.
- `GET /geo/hazards`: Identified hazard points and areas.
- `GET /geo/routes`: Evacuation and utility corridors.
- `GET /geo/evacuation`: Evacuation paths to assembly points.
- `GET /geo/exposure`: Worker and equipment exposure radii.
- `GET /geo/clusters`: Grouped spatial risk clusters.
- `GET /geo/resources`: Emergency exits and safe assembly zones.
- `GET /geo/nearest-safe-zone`: Computes the shortest safe path from a risk anchor.

## 4. Operational Flow
1. **Event Ingestion**: IoT sensors, SCADA, and manual inputs stream into the Event Platform.
2. **Context & Graph Updates**: Digital Twin state is updated; Knowledge Graph models relational dependencies.
3. **Deterministic Risk Evaluation**: The Compound Risk Engine calculates baseline scores.
4. **Intelligence Enrichment**: The RAG pipeline and specialized agents fetch historical and regulatory context.
5. **Geospatial Projection**: Risk vectors and physical constraints are mapped via spatial analytics.
6. **Action & Notification**: Actions are queued to the Transactional Outbox and emitted via Kafka.

## 5. Developer Guide
- **Setup**: Run `docker compose up --build` to stand up the API, PostgreSQL DB, and Kafka.
- **Testing**: Use `pytest` for the comprehensive test suite spanning unit tests, integration tests, spatial tests, and RAG validation.
- **Observability**: RAG and API latencies, vector queries, agent execution times, and document ingestion are actively monitored via metrics.

## 6. Deployment Guide
- Standard Docker-compose setup for single-node deployment.
- Environment variables must be mapped as per `.env.example`.
- Pre-seeded default corpus handles initial compliance logic, but dynamic documents can be ingested via the `/intelligence/` APIs.
