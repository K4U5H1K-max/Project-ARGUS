import { ChapterSection } from "@/components/chapters/ChapterSection";
import { GraphViz } from "@/components/viz/GraphViz";

export function KnowledgeGraphSection() {
  return (
    <ChapterSection
      id="knowledge-graph"
      eyebrow="Knowledge Graph"
      title="See the blast radius before it spreads"
      description="Fragmented alarms miss the pattern. ARGUS correlates a gas cloud, a hot-work permit, and downstream equipment dependencies into one impact path — so you see which workers, zones, and assets sit inside the blast radius before the hazard cascades. That alarm-correlation story is the difference between a near miss and an incident."
      visual={<GraphViz />}
      spacing="featured"
    />
  );
}
