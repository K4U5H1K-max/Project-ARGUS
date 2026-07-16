import { ChapterSection } from "@/components/chapters/ChapterSection";
import { ReliabilityConsoleViz } from "@/components/viz/ReliabilityConsoleViz";

export function ReliabilitySection() {
  return (
    <ChapterSection
      id="reliability"
      eyebrow="Reliability"
      title="Engineering quality you can verify"
      description="ARGUS is built for production. Idempotent ingestion via processed_events ledger. Transactional outbox with retry and dead-lettering. Kafka event pipeline. Neo4j graph sync with revision tracking. Health, readiness, and Prometheus metrics endpoints."
      visual={<ReliabilityConsoleViz />}
      spacing="chapter"
    />
  );
}
