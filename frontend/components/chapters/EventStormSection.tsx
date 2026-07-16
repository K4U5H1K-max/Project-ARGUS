import { ChapterSection } from "@/components/chapters/ChapterSection";
import { EventStreamViz } from "@/components/viz/EventStreamViz";
import { PipelineSimulator } from "@/components/viz/PipelineSimulator";

export function EventStormSection() {
  return (
    <ChapterSection
      id="pipeline"
      eyebrow="Event Storm"
      title="Every signal enters one pipeline"
      description="ARGUS ingests heterogeneous events through a single, idempotent ingestion path. Gas sensors, permit changes, vision detections, equipment telemetry, worker movements, and incident reports all flow into the platform — duplicates are silently claimed and skipped."
      visual={
        <div className="space-y-4">
          <EventStreamViz />
          <PipelineSimulator />
        </div>
      }
      spacing="featured"
    />
  );
}
