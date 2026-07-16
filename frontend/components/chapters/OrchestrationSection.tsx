import { ChapterSection } from "@/components/chapters/ChapterSection";
import { OrchestrationWorkflowViz } from "@/components/viz/OrchestrationWorkflowViz";

export function OrchestrationSection() {
  return (
    <ChapterSection
      id="orchestration"
      eyebrow="Operational Orchestration"
      title="One coordinated response"
      description="Detection triggers assessment. Assessment triggers action. Emergency incidents progress through defined lifecycles. Permits are scanned for conflicts. Compliance violations are flagged. Notifications dispatch across channels. Vision and predictive modules feed the same pipeline."
      visual={<OrchestrationWorkflowViz />}
      reverse
      spacing="chapter"
    />
  );
}
