"use client";

import { m } from "framer-motion";
import { useState } from "react";

import { TWIN_ENTITIES, type TwinEntity } from "@/lib/content/story";
import { Badge } from "@/components/ui/Badge";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { cn } from "@/lib/utils/cn";

const typeColors: Record<TwinEntity["type"], string> = {
  zone: "text-accent-cyan",
  equipment: "text-signal-info",
  worker: "text-signal-safe",
  sensor: "text-signal-warning",
};

/** Interactive digital twin topology — entity selection reveals state. */
export function TwinTopologyViz({ className }: { className?: string }) {
  const [selected, setSelected] = useState<TwinEntity>(TWIN_ENTITIES[0]);

  const nodeMap: Record<string, { x: number; y: number }> = {
    Battery_A: { x: 120, y: 80 },
    "eq-compressor-01": { x: 50, y: 150 },
    "wkr-4421": { x: 190, y: 150 },
    "sns-gas-07": { x: 120, y: 200 },
  };

  return (
    <div className={cn("relative w-full", className)}>
      <Panel active className="relative overflow-hidden p-4 md:p-6">
        <BlueprintOverlay patternId="twin-grid" />

        <p className="relative mb-3 font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
          GET /twin/* — Live Operational State
        </p>

        <svg
          viewBox="0 0 240 230"
          className="mx-auto h-48 w-full max-w-[280px]"
          aria-label="Digital twin plant topology"
          role="img"
        >
          <m.polygon
            points="120,30 200,70 200,170 40,170 40,70"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            className="text-accent-cyan/40"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.2 }}
          />

          {[
            ["120", "80", "50", "150"],
            ["120", "80", "190", "150"],
            ["120", "80", "120", "200"],
            ["50", "150", "120", "200"],
          ].map(([x1, y1, x2, y2], i) => (
            <m.line
              key={i}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="currentColor"
              strokeWidth="1"
              className="text-accent-violet/30"
              initial={{ pathLength: 0 }}
              whileInView={{ pathLength: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 + i * 0.1, duration: 0.5 }}
            />
          ))}

          {TWIN_ENTITIES.map((entity) => {
            const pos = nodeMap[entity.id];
            const isSelected = selected.id === entity.id;
            return (
              <g
                key={entity.id}
                className="cursor-pointer"
                onClick={() => setSelected(entity)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") setSelected(entity);
                }}
                role="button"
                tabIndex={0}
                aria-label={`Select ${entity.label}`}
                aria-pressed={isSelected}
              >
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={isSelected ? 10 : 7}
                  className={cn(
                    "transition-all duration-300",
                    isSelected
                      ? "fill-accent-cyan/20 stroke-accent-cyan"
                      : "fill-bg-surface stroke-border-subtle",
                  )}
                  strokeWidth="1.5"
                />
                <text
                  x={pos.x}
                  y={pos.y + 20}
                  textAnchor="middle"
                  className="fill-text-muted font-mono text-[7px]"
                >
                  {entity.type}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Entity detail panel — API-ready shape */}
        <m.div
          key={selected.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 rounded-chip border border-border-subtle bg-bg-surface/80 p-3"
        >
          <div className="flex items-center justify-between">
            <span className={cn("font-mono text-sm", typeColors[selected.type])}>
              {selected.label}
            </span>
            <Badge
              level={
                selected.status === "ALERT"
                  ? "warning"
                  : selected.status === "RUNNING" || selected.status === "ACTIVE"
                    ? "safe"
                    : "info"
              }
            >
              {selected.status}
            </Badge>
          </div>
          <div className="mt-2 grid grid-cols-2 gap-2 font-mono text-[10px] text-text-muted">
            <span>plant: {selected.plant_id}</span>
            <span>zone: {selected.zone_id}</span>
            <span>version: {selected.version}</span>
            <span>type: {selected.type}</span>
          </div>
        </m.div>
      </Panel>
    </div>
  );
}
