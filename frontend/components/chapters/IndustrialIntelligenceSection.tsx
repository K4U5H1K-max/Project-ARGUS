import { ChapterSection } from "@/components/chapters/ChapterSection";
import { IntelligenceReportViz } from "@/components/viz/IntelligenceReportViz";

export function IndustrialIntelligenceSection() {
  return (
    <ChapterSection
      id="intelligence"
      eyebrow="Industrial Intelligence"
      title="Grounded AI with citations"
      description="ARGUS enriches risk assessments with document retrieval, regulation lookups, root cause analysis, and citation-backed recommendations. Every insight traces to a source — OISD guidance, incident reports, and operational procedures."
      visual={<IntelligenceReportViz />}
      spacing="featured"
    />
  );
}
