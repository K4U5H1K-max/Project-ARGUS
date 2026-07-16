import { ChapterSection } from "@/components/chapters/ChapterSection";
import { ConvergenceViz } from "@/components/viz/ConvergenceViz";

export function ChallengeSection() {
  return (
    <ChapterSection
      id="challenge"
      eyebrow="The Challenge"
      title="Operational blind spots at industrial scale"
      description="A mid-size process plant can emit 50,000+ heterogeneous signals per day — gas sensors, vision detections, worker movements, equipment telemetry, permits, and emergency incidents. Without unified correlation, those streams become operational blind spots: alarms fire in isolation, and the blast radius stays invisible until it is too late."
      visual={<ConvergenceViz />}
      connector={false}
      spacing="chapter"
    />
  );
}
