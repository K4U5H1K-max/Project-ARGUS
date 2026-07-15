# Phase 4: Knowledge Graph

The `app.graph` package is an isolated Neo4j adapter. The Digital Twin remains the source of operational state; the graph is the canonical relationship projection for querying future risk and AI services.

Each accepted event incrementally merges `GraphEntity` nodes and typed relationships, then appends a `GraphRevision` record keyed to the source event. No graph rebuild occurs during normal event processing. Replays call the same synchronization path and write revision metadata with `replay=true`.

Neo4j bootstrapping creates an identity constraint on `(node_type, node_id)` and an event revision index. Run the supplied Docker Compose stack or configure `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE` for a managed cluster.

The operational API is rooted at `/graph`: node lookup, neighbors, shortest paths, radius, zone/equipment/worker views, impact/dependency traversal, worker exposure, and permit overlaps. Relationship labels are strictly enum-derived; user input is passed as Cypher parameters.
