import { Badge } from "@/components/ui/Badge";

const indicators = [
  {
    label: "Idempotent ingestion",
    level: "info" as const,
  },
  {
    label: "Transactional outbox",
    level: "safe" as const,
  },
  {
    label: "Explainable risk",
    level: "warning" as const,
  },
  {
    label: "Neo4j knowledge graph",
    level: "info" as const,
  },
];

/** Trust / credibility markers beneath the hero CTAs. */
export function TrustIndicators() {
  return (
    <div className="space-y-3">
      <p className="text-center font-mono text-[10px] uppercase tracking-[0.2em] text-text-muted lg:text-left">
        Built for production systems
      </p>
      <div className="flex flex-wrap items-center justify-center gap-2 lg:justify-start">
        {indicators.map((item) => (
          <Badge key={item.label} level={item.level}>
            {item.label}
          </Badge>
        ))}
      </div>
    </div>
  );
}
