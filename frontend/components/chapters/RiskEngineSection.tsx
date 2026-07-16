import { ChapterSection } from "@/components/chapters/ChapterSection";
import { RiskSurfaceViz } from "@/components/viz/RiskSurfaceViz";

export function RiskEngineSection() {
  return (
    <ChapterSection
      id="risk"
      eyebrow="AI Risk Engine"
      title="Deterministic, explainable risk"
      description="ARGUS produces persisted risk assessments with scores, confidence levels, spatial exposure, and evidence-backed explanations. Every assessment includes contributing rules, affected entities, and deterministic recommendations — not black-box predictions."
      visual={<RiskSurfaceViz />}
      reverse
      spacing="featured"
    />
  );
}
