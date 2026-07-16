import { ChapterSection } from "@/components/chapters/ChapterSection";
import { ContextLensViz } from "@/components/viz/ContextLensViz";

export function ContextEngineSection() {
  return (
    <ChapterSection
      id="context-engine"
      eyebrow="Context Engine"
      title="Operational awareness, not just data"
      description="The Context Engine assembles workers, permits, equipment status, and active hazards into a single operational snapshot. It answers the question every safety officer asks: what matters right now in this zone?"
      visual={<ContextLensViz />}
      spacing="chapter"
    />
  );
}
