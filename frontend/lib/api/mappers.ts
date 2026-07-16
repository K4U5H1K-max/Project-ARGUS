import type { GeoLayoutResponse, HealthResponse, RiskApiResponse } from "@/lib/api/types";
import type { HealthStatus, RiskAssessment } from "@/lib/content/story";

export function mapHealthToStatus(health: HealthResponse): HealthStatus {
  return {
    status: health.status === "ok" ? "ok" : "degraded",
    database: health.database,
    kafka: health.kafka,
    outbox_worker: health.outbox_worker,
    neo4j: health.neo4j,
    replay_service: health.replay_service,
  };
}

export function mapRiskApiToAssessment(
  risk: RiskApiResponse,
): RiskAssessment {
  const trace = risk.trace ?? {};
  const evidenceRaw = Array.isArray(trace.contributing_rules)
    ? trace.contributing_rules
    : [];

  const evidence =
    evidenceRaw.length > 0
      ? evidenceRaw.map((rule: Record<string, unknown>, i: number) => ({
          rule_id: String(rule.rule_id ?? rule.id ?? `rule-${i}`),
          description: String(rule.description ?? rule.explanation ?? "Rule matched"),
          confidence: Number(rule.confidence ?? 0.8),
        }))
      : [
          {
            rule_id: "compound_engine",
            description: risk.explanation ?? "Risk assessment generated",
            confidence: risk.confidence,
          },
        ];

  return {
    risk_id: risk.risk_id,
    plant_id: risk.plant_id,
    zone_id: risk.zone_id,
    risk_score: risk.score,
    risk_level: (["CRITICAL", "HIGH", "MODERATE"].includes(risk.level)
      ? risk.level
      : "MODERATE") as RiskAssessment["risk_level"],
    confidence: risk.confidence,
    explanation: risk.explanation ?? "Risk assessment active for zone.",
    recommendations: risk.recommendations ?? [],
    evidence,
  };
}

export function extractGeoZoneLabels(layout: GeoLayoutResponse): string[] {
  return layout.features
    .map((f) => String(f.properties.label ?? f.properties.zone_id ?? f.properties.name ?? ""))
    .filter(Boolean)
    .slice(0, 6);
}
