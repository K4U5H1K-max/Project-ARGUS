import { ChapterSection } from "@/components/chapters/ChapterSection";
import { GeoLayoutViz } from "@/components/viz/GeoLayoutViz";

export function GeoIntelligenceSection() {
  return (
    <ChapterSection
      id="geo-intelligence"
      eyebrow="Geo Intelligence"
      title="Decisions in space"
      description="Risk isn't abstract — it has a location. ARGUS projects plant layouts, hazard heatmaps, evacuation routes, safe assembly points, and exposure zones as MapLibre-ready spatial intelligence. Where is the danger? Where is safety?"
      visual={<GeoLayoutViz />}
      reverse
      spacing="chapter"
    />
  );
}
