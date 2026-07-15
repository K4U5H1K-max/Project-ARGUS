# Phase 7 Architecture Document

Phase 7 of Project ARGUS extends the foundational Risk Engine into an Autonomous Safety Operations Platform. It introduces orchestration, intelligent compliance, digital permit analysis, and a robust notification framework without altering the deterministic Compound Risk Engine established in previous phases.

## 1. Bounded Contexts Added

### 1.1 Emergency Orchestrator (`app.emergency`)
- **Responsibility**: Manages the lifecycle of an emergency from Detection through Resolution.
- **Components**: 
  - `IncidentManagerAgent` safely transitions the incident state.
  - `EmergencyResponseAgent` dynamically attaches `EmergencyPlaybooks` to active incidents based on detected hazards.
  - `ResourceAllocationAgent` optimizes the dispatch of safety resources (Fire Teams, HAZMAT).

### 1.2 Digital Permit Intelligence (`app.permit`)
- **Responsibility**: Continuously evaluates overlapping spatial permits to detect unsafe simultaneous operations.
- **Components**:
  - Leverages the `GraphQueryService` to query adjacency.
  - Analyzes active context snapshots to identify if required PPE and isolation states are met for High-Risk Permits (e.g., Hot Work).

### 1.3 Compliance Intelligence (`app.compliance`)
- **Responsibility**: Runs background checks on the `ContextSnapshot` to ensure alignment with OISD and Factory Act safety standards.
- **Components**:
  - Detects if active workers are missing specific training records or PPE relative to their zone's known hazards.

### 1.4 Notification Framework (`app.notifications`)
- **Responsibility**: Unified routing of priority alerts.
- **Components**:
  - `NotificationCoordinator` dispatches messages sequentially to Kafka, WebSockets, Email, and SMS based on priority. Provides tracking for Acknowledgements and Escalations.

## 2. Integration Points
The existing `ActionEngine` (`app.actions`) has been extended with an **ActionPlanner**. Instead of just generating individual `ActionEvents`, it now sequences them into structured `ActionPlans` complete with dependencies, deadlines, and assigned teams.
