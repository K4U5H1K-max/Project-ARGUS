"use client";

import { m } from "framer-motion";
import { memo } from "react";

import { useHealth } from "@/hooks/useHealth";
import { useReadiness } from "@/hooks/useReadiness";
import { RELIABILITY_CONCEPTS } from "@/lib/content/story";
import { Badge } from "@/components/ui/Badge";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { transitionBase } from "@/lib/animations/variants";
import { cn } from "@/lib/utils/cn";

/** Engineering reliability console — live health + readiness with fallback. */
export const ReliabilityConsoleViz = memo(function ReliabilityConsoleViz({
  className,
}: {
  className?: string;
}) {
  const healthQuery = useHealth();
  const readinessQuery = useReadiness();
  const health = healthQuery.data;
  const isLive = healthQuery.isLive || readinessQuery.isLive;

  const statusItems = [
    { label: "PostgreSQL", ok: health.database },
    { label: "Kafka", ok: health.kafka },
    { label: "Outbox Worker", ok: health.outbox_worker },
    { label: "Neo4j", ok: health.neo4j },
    { label: "Replay Service", ok: health.replay_service },
  ] as const;

  return (
    <div className={cn("relative w-full", className)}>
      <Panel className="relative overflow-hidden p-4 md:p-6">
        <BlueprintOverlay patternId="reliability-grid" />

        <div className="relative mb-4 flex flex-wrap items-center justify-between gap-2">
          <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
            GET /health · /readiness · /metrics
          </p>
          {isLive ? (
            <span className="font-mono text-[10px] uppercase tracking-wider text-signal-safe">
              Live
            </span>
          ) : null}
        </div>

          <div className="relative mb-4 flex flex-wrap items-center gap-3">
            <Badge level={readinessQuery.isReady ? "safe" : "warning"}>
              {readinessQuery.isReady ? "READY" : "DEGRADED"}
            </Badge>
            <Badge level={health.status === "ok" ? "safe" : "warning"}>
              {health.status.toUpperCase()}
            </Badge>
            <span className="font-mono text-xs text-text-muted">
              System readiness
            </span>
          </div>

          <div className="relative grid grid-cols-2 gap-2 sm:grid-cols-3">
            {statusItems.map((item, i) => (
              <m.div
                key={item.label}
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ ...transitionBase, delay: i * 0.06 }}
                className={cn(
                  "rounded-chip border px-3 py-2",
                  item.ok
                    ? "border-signal-safe/30 bg-signal-safe/5"
                    : "border-signal-critical/30 bg-signal-critical/5",
                )}
              >
                <p className="font-mono text-[10px] text-text-muted">
                  {item.label}
                </p>
                <p
                  className={cn(
                    "font-mono text-xs",
                    item.ok ? "text-signal-safe" : "text-signal-critical",
                  )}
                >
                  {item.ok ? "READY" : "DOWN"}
                </p>
              </m.div>
            ))}
          </div>

          <div className="relative mt-6 space-y-2">
            {RELIABILITY_CONCEPTS.map((concept, i) => (
              <m.div
                key={concept.label}
                initial={{ opacity: 0, x: -8 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ ...transitionBase, delay: 0.2 + i * 0.08 }}
                className="rounded-chip border border-border-subtle bg-bg-surface/60 px-3 py-2"
              >
                <p className="font-mono text-xs text-accent-cyan">
                  {concept.label}
                </p>
                <p className="font-mono text-[10px] text-text-muted">
                  {concept.detail}
                </p>
              </m.div>
            ))}
          </div>

          <p className="relative mt-4 font-mono text-[10px] text-text-muted">
            {isLive
              ? "Live telemetry from backend health endpoints"
              : "Sample reliability profile — connect backend to view live status"}
          </p>
      </Panel>
    </div>
  );
});
