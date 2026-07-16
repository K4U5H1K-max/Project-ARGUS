import dynamic from "next/dynamic";

import { ChallengeSection } from "./ChallengeSection";
import { DigitalTwinSection } from "./DigitalTwinSection";
import { EventStormSection } from "./EventStormSection";
import { Skeleton } from "@/components/ui/Skeleton";

function SectionFallback() {
  return (
    <div className="py-20 md:py-28" aria-hidden>
      <div className="mx-auto max-w-content px-6 md:px-8">
        <Skeleton className="mb-6 h-8 w-48" />
        <Skeleton className="mb-4 h-12 w-full max-w-lg" />
        <Skeleton className="h-64 w-full" />
      </div>
    </div>
  );
}

const ContextEngineSection = dynamic(
  () =>
    import("./ContextEngineSection").then((m) => ({
      default: m.ContextEngineSection,
    })),
  { loading: () => <SectionFallback /> },
);

const RiskEngineSection = dynamic(
  () =>
    import("./RiskEngineSection").then((m) => ({
      default: m.RiskEngineSection,
    })),
  { loading: () => <SectionFallback /> },
);

const KnowledgeGraphSection = dynamic(
  () =>
    import("./KnowledgeGraphSection").then((m) => ({
      default: m.KnowledgeGraphSection,
    })),
  { loading: () => <SectionFallback /> },
);

const GeoIntelligenceSection = dynamic(
  () =>
    import("./GeoIntelligenceSection").then((m) => ({
      default: m.GeoIntelligenceSection,
    })),
  { loading: () => <SectionFallback /> },
);

const IndustrialIntelligenceSection = dynamic(
  () =>
    import("./IndustrialIntelligenceSection").then((m) => ({
      default: m.IndustrialIntelligenceSection,
    })),
  { loading: () => <SectionFallback /> },
);

const OrchestrationSection = dynamic(
  () =>
    import("./OrchestrationSection").then((m) => ({
      default: m.OrchestrationSection,
    })),
  { loading: () => <SectionFallback /> },
);

const ReliabilitySection = dynamic(
  () =>
    import("./ReliabilitySection").then((m) => ({
      default: m.ReliabilitySection,
    })),
  { loading: () => <SectionFallback /> },
);

const FinalCTASection = dynamic(
  () =>
    import("./FinalCTASection").then((m) => ({
      default: m.FinalCTASection,
    })),
  { loading: () => <SectionFallback /> },
);

/**
 * Complete landing page narrative — continuous pipeline story
 * from industrial challenge through to final call to action.
 */
export function StoryPipeline() {
  return (
    <>
      <ChallengeSection />
      <EventStormSection />
      <DigitalTwinSection />
      <ContextEngineSection />
      <RiskEngineSection />
      <KnowledgeGraphSection />
      <GeoIntelligenceSection />
      <IndustrialIntelligenceSection />
      <OrchestrationSection />
      <ReliabilitySection />
      <FinalCTASection />
    </>
  );
}
