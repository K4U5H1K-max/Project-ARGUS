"use client";

import { m } from "framer-motion";
import { memo, useState } from "react";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { useRiskCurrent } from "@/hooks/useRiskCurrent";
import { Badge } from "@/components/ui/Badge";
import { Metric } from "@/components/ui/Metric";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { transitionBase } from "@/lib/animations/variants";
import { cn } from "@/lib/utils/cn";

const levelMap = {
  CRITICAL: "critical",
  HIGH: "warning",
  MODERATE: "info",
} as const;

/** Risk score, evidence, heatmap propagation — always shows data (live or sample). */
export const RiskSurfaceViz = memo(function RiskSurfaceViz({
  className,
}: {
  className?: string;
}) {
  const reduced = useReducedMotion();
  const [expanded, setExpanded] = useState(true);
  const { data: risk, isLive } = useRiskCurrent();
  const badgeLevel =
    levelMap[risk.risk_level as keyof typeof levelMap] ?? "info";

  return (
    <div className={cn("relative w-full", className)}>
      <Panel
        active
        glow={risk.risk_level === "CRITICAL" ? "critical" : "cyan"}
        className="relative overflow-hidden p-4 md:p-6"
      >
        <BlueprintOverlay patternId="risk-grid" />

        <div className="relative mb-4 flex flex-wrap items-center justify-between gap-2">
          <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
            GET /risk/current — Deterministic Risk Engine
          </p>
          {isLive ? (
            <span className="font-mono text-[10px] uppercase tracking-wider text-signal-safe">
              Live
            </span>
          ) : null}
        </div>

        <div className="relative grid gap-4 md:grid-cols-2">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Badge level={badgeLevel}>{risk.risk_level}</Badge>
                <span className="font-mono text-xs text-text-muted">
                  {Math.round(risk.confidence * 100)}% confidence
                </span>
              </div>
              <Metric
                label="Risk Score"
                value={String(risk.risk_score)}
                unit="/100"
                trend="up"
              />
              <p className="text-sm leading-relaxed text-text-secondary">
                {risk.explanation}
              </p>
              <p className="font-mono text-[10px] text-text-muted">
                Plant {risk.plant_id} · Zone {risk.zone_id} · {risk.risk_id}
              </p>
              <button
                type="button"
                onClick={() => setExpanded((e) => !e)}
                className="rounded-sm font-mono text-xs text-accent-cyan hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-cyan/50"
                aria-expanded={expanded}
              >
                {expanded ? "Hide explainability" : "Show explainability"}
              </button>
            </div>

            <div className="relative min-h-[10rem]">
              <svg
                viewBox="0 0 200 160"
                className="h-40 w-full"
                aria-label={`Risk heatmap for zone ${risk.zone_id}`}
                role="img"
              >
                <rect
                  x="20"
                  y="20"
                  width="160"
                  height="120"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-accent-cyan/30"
                  rx="4"
                />
                <text
                  x="100"
                  y="14"
                  textAnchor="middle"
                  className="fill-text-muted font-mono text-[8px]"
                >
                  {risk.zone_id}
                </text>
                <defs>
                  <radialGradient id="risk-heat-live">
                    <stop
                      offset="0%"
                      stopColor="var(--signal-critical)"
                      stopOpacity="0.6"
                    />
                    <stop
                      offset="100%"
                      stopColor="var(--signal-critical)"
                      stopOpacity="0"
                    />
                  </radialGradient>
                </defs>
                <m.ellipse
                  cx="100"
                  cy="80"
                  rx="15"
                  ry="12"
                  fill="url(#risk-heat-live)"
                  initial={{ rx: 0, ry: 0, opacity: 0 }}
                  whileInView={{ rx: 55, ry: 40, opacity: 1 }}
                  viewport={{ once: true, margin: "-40px" }}
                  transition={{ duration: 1.2, ease: [0.2, 0, 0, 1] }}
                />
                {[30, 50, 70].map((r, i) => (
                  <m.circle
                    key={r}
                    cx="100"
                    cy="80"
                    r={r * 0.4}
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="0.5"
                    className="text-signal-critical/30"
                    initial={{ scale: 0, opacity: 0 }}
                    whileInView={{ scale: 1, opacity: 0.6 }}
                    viewport={{ once: true, margin: "-40px" }}
                    transition={{
                      delay: reduced ? 0 : 0.4 + i * 0.25,
                      duration: 0.7,
                    }}
                  />
                ))}
                <m.circle
                  cx="100"
                  cy="80"
                  r="4"
                  className="fill-signal-critical"
                  animate={reduced ? undefined : { opacity: [1, 0.4, 1] }}
                  transition={
                    reduced ? undefined : { duration: 2.5, repeat: Infinity }
                  }
                />
              </svg>
            </div>
          </div>

          <m.div
            initial={false}
            animate={{
              height: expanded ? "auto" : 0,
              opacity: expanded ? 1 : 0,
            }}
            transition={transitionBase}
            className="overflow-hidden"
          >
            <div className="mt-4 space-y-2 border-t border-border-subtle pt-4">
              <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
                Contributing Rules
              </p>
              {risk.evidence.map((rule, i) => (
                <m.div
                  key={rule.rule_id}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ ...transitionBase, delay: i * 0.08 }}
                  className="rounded-chip border border-border-subtle bg-bg-surface/60 p-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-accent-cyan">
                      {rule.rule_id}
                    </span>
                    <span className="font-mono text-[10px] text-text-muted">
                      {Math.round(rule.confidence * 100)}%
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-text-secondary">
                    {rule.description}
                  </p>
                </m.div>
              ))}
            </div>
          </m.div>

          <div className="relative mt-4 space-y-1">
            <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
              Recommendations
            </p>
            {risk.recommendations.map((rec) => (
              <p key={rec} className="text-xs text-text-secondary">
                → {rec}
              </p>
            ))}
          </div>
      </Panel>
    </div>
  );
});
