# Project ARGUS: Operational Runbook

## Emergency Incident Management
If an incident escalates beyond auto-mitigation, the operations team must manually transition the incident state.
- **API**: `POST /emergency/incidents/{incident_id}/transition`
- **Expected States**: DETECTED → VALIDATED → DECLARED → RESPONSE_STARTED → EVACUATION → CONTAINMENT → RECOVERY → RESOLVED → ARCHIVED

## Resolving Permit Conflicts
If simultaneous operations (e.g. Hot Work + Chemical Wash) trigger a conflict, safety officers must override or cancel one of the permits.
- **API**: `POST /permit/resolve/{conflict_id}`

## Managing Notifications
If SMS/Kafka queues fail, notifications might stall in a `DISPATCHED` state.
- Acknowledge a notification manually to stop escalations.
- **API**: `POST /notifications/{notification_id}/acknowledge`

## Compliance Auditing
- Review unresolved violations via the Dashboard. Violations are automatically generated if context snapshots detect workers operating without required PPE (e.g. Missing Gas Mask in Hot Work).
