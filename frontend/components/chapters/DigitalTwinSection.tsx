import { ChapterSection } from "@/components/chapters/ChapterSection";
import { TwinTopologyViz } from "@/components/viz/TwinTopologyViz";

export function DigitalTwinSection() {
  return (
    <ChapterSection
      id="digital-twin"
      eyebrow="Digital Twin"
      title="A living model of your facility"
      description="Every accepted event updates a versioned Digital Twin — the canonical operational state of plants, zones, equipment, workers, sensors, permits, and hazards. ARGUS doesn't just receive data; it maintains the truth of what is happening right now."
      visual={<TwinTopologyViz />}
      reverse
      spacing="chapter"
    />
  );
}
