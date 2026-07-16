"use client";

import { m } from "framer-motion";
import { memo, useMemo, useState } from "react";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { useGeoLayout } from "@/hooks/useGeoLayout";
import { GEO_ZONES } from "@/lib/content/story";
import { Badge } from "@/components/ui/Badge";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { extractGeoZoneLabels } from "@/lib/api/mappers";
import { cn } from "@/lib/utils/cn";

const SCENARIOS = [
  { id: "gas", label: "Gas Cloud" },
  { id: "hotwork", label: "Hot Work" },
] as const;

/** Plant layout with evacuation routes — live geo layout with SVG fallback. */
export const GeoLayoutViz = memo(function GeoLayoutViz({
  className,
}: {
  className?: string;
}) {
  const reduced = useReducedMotion();
  const [scenario, setScenario] =
    useState<(typeof SCENARIOS)[number]["id"]>("gas");
  const { layout, isLive } = useGeoLayout();

  const routePath =
    scenario === "gas"
      ? "M 40 140 Q 80 100 120 80 T 200 60"
      : "M 160 140 Q 120 100 80 80 T 40 60";

  const zoneLabels = useMemo(() => {
    if (layout?.features?.length) {
      const labels = extractGeoZoneLabels(layout);
      return labels.length > 0 ? labels : GEO_ZONES.map((z) => z.label);
    }
    return GEO_ZONES.map((z) => z.label);
  }, [layout]);

  const summary = layout?.summary;

  return (
    <div className={cn("relative w-full", className)}>
      <Panel active glow="cyan" className="relative overflow-hidden p-4 md:p-6">
        <BlueprintOverlay patternId="geo-grid" />

        <div className="relative mb-3 flex flex-wrap items-center justify-between gap-2">
          <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
            GET /geo/layout — Spatial Intelligence
          </p>
          {isLive ? (
            <span className="font-mono text-[10px] uppercase tracking-wider text-signal-safe">
              Live
            </span>
          ) : null}
        </div>

        <div className="relative mb-4 flex gap-2">
          {SCENARIOS.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => setScenario(s.id)}
              className={cn(
                "rounded-chip border px-3 py-1 font-mono text-xs transition-all duration-300",
                scenario === s.id
                  ? "border-accent-cyan/40 bg-accent-cyan/10 text-accent-cyan"
                  : "border-border-subtle text-text-secondary hover:border-accent-cyan/20",
              )}
              aria-pressed={scenario === s.id}
            >
              {s.label}
            </button>
          ))}
        </div>

          <svg
            viewBox="0 0 240 180"
            className="h-44 w-full min-h-[11rem]"
            aria-label="Plant layout with evacuation route and hazard overlays"
            role="img"
          >
            <rect
              x="30"
              y="40"
              width="80"
              height="60"
              fill="none"
              stroke="currentColor"
              strokeWidth="1"
              className="text-accent-cyan/40"
              rx="2"
            />
            <rect
              x="130"
              y="50"
              width="70"
              height="50"
              fill="none"
              stroke="currentColor"
              strokeWidth="1"
              className="text-accent-cyan/30"
              rx="2"
            />

            {isLive &&
              layout?.features?.slice(0, 4).map((_, i) => {
                const x = 30 + (i % 2) * 100 + 40;
                const y = 50 + Math.floor(i / 2) * 30;
                return (
                  <circle
                    key={`geo-feature-${i}`}
                    cx={x}
                    cy={y}
                    r="3"
                    className="fill-accent-cyan/60"
                    aria-hidden
                  />
                );
              })}

            <m.circle
              cx="70"
              cy="70"
              r="20"
              fill="none"
              stroke="currentColor"
              strokeWidth="1"
              className="text-signal-critical/40"
              animate={
                reduced || scenario !== "gas"
                  ? undefined
                  : { r: [15, 30, 15], opacity: [0.6, 0.2, 0.6] }
              }
              transition={
                reduced ? undefined : { duration: 3.5, repeat: Infinity }
              }
            />

            <m.path
              key={scenario}
              d={routePath}
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="text-signal-safe"
              strokeDasharray="6 4"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1.2, ease: [0.2, 0, 0, 1] }}
            />

            <circle
              cx="200"
              cy="60"
              r="6"
              className="fill-signal-safe/30 stroke-signal-safe"
              strokeWidth="1.5"
            />
            <text
              x="200"
              y="50"
              textAnchor="middle"
              className="fill-signal-safe font-mono text-[7px]"
            >
              SAFE
            </text>
            <text
              x="70"
              y="75"
              textAnchor="middle"
              className="fill-text-muted font-mono text-[8px]"
            >
              {zoneLabels[0] ?? "Battery A"}
            </text>
            <text
              x="165"
              y="78"
              textAnchor="middle"
              className="fill-text-muted font-mono text-[8px]"
            >
              {zoneLabels[1] ?? "Assembly"}
            </text>
          </svg>

          <div className="relative mt-4 flex flex-wrap gap-2">
            {(isLive ? zoneLabels : GEO_ZONES.map((z) => z.label)).map(
              (label, i) => (
                <Badge
                  key={`${label}-${i}`}
                  level={
                    GEO_ZONES[i]?.risk_level ??
                    (i === 0 ? "critical" : i === 1 ? "warning" : "info")
                  }
                >
                  {label}
                </Badge>
              ),
            )}
          </div>

          <p className="relative mt-3 font-mono text-[10px] text-text-muted">
            {summary
              ? `Plant ${summary.plant_id} · Zone ${summary.zone_id} · ${summary.feature_count} features`
              : "Nearest safe zone: Assembly North · 120m"}
          </p>
      </Panel>
    </div>
  );
});
