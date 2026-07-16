"use client";

import { m } from "framer-motion";
import { useState } from "react";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { CONTEXT_SNAPSHOT } from "@/lib/content/story";
import { Badge } from "@/components/ui/Badge";
import { Chip } from "@/components/ui/Chip";
import { Metric } from "@/components/ui/Metric";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { cn } from "@/lib/utils/cn";

const LAYERS = [
  { key: "workers", label: "Workers", delay: 0 },
  { key: "permits", label: "Permits", delay: 0.15 },
  { key: "equipment", label: "Equipment", delay: 0.3 },
  { key: "hazards", label: "Hazards", delay: 0.45 },
] as const;

/** Context layers assembling into one operational snapshot. */
export function ContextLensViz({ className }: { className?: string }) {
  const reduced = useReducedMotion();
  const [activeLayers, setActiveLayers] = useState<string[]>([]);
  const [scrub, setScrub] = useState(100);

  const toggleLayer = (key: string) => {
    setActiveLayers((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key],
    );
  };

  const allActive = activeLayers.length === LAYERS.length;

  return (
    <div className={cn("relative w-full", className)}>
      <Panel glow="violet" className="relative overflow-hidden p-4 md:p-6">
        <BlueprintOverlay patternId="context-grid" />

        <p className="relative mb-4 font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
          GET /contexts/latest — Operational Snapshot
        </p>

        {/* Layer toggles */}
        <div className="relative mb-4 flex flex-wrap gap-2">
          {LAYERS.map((layer) => {
            const active = activeLayers.includes(layer.key);
            return (
              <button
                key={layer.key}
                type="button"
                onClick={() => toggleLayer(layer.key)}
                className={cn(
                  "rounded-chip border px-3 py-1 font-mono text-xs transition-all duration-300",
                  active
                    ? "border-accent-violet/40 bg-accent-violet/10 text-accent-violet"
                    : "border-border-subtle bg-bg-surface/60 text-text-secondary hover:border-accent-violet/20",
                )}
                aria-pressed={active}
              >
                {layer.label}
              </button>
            );
          })}
          <button
            type="button"
            onClick={() =>
              setActiveLayers(
                activeLayers.length === LAYERS.length
                  ? []
                  : LAYERS.map((l) => l.key),
              )
            }
            className="rounded-chip border border-border-subtle px-3 py-1 font-mono text-xs text-text-muted hover:text-accent-cyan"
          >
            {allActive ? "Clear" : "All layers"}
          </button>
        </div>

        {/* Assembling lens visualization */}
        <div className="relative mx-auto h-40 w-full max-w-[280px]">
          {LAYERS.map((layer) => {
            const active = activeLayers.includes(layer.key);
            return (
              <m.div
                key={layer.key}
                className={cn(
                  "absolute inset-4 rounded-panel border",
                  layer.key === "workers" && "border-signal-safe/30",
                  layer.key === "permits" && "border-signal-info/30",
                  layer.key === "equipment" && "border-accent-cyan/30",
                  layer.key === "hazards" && "border-signal-critical/30",
                )}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{
                  opacity: active ? 0.6 : 0,
                  scale: active ? 1 : 0.9,
                }}
                transition={{
                  delay: reduced ? 0 : layer.delay,
                  duration: 0.5,
                }}
              />
            );
          })}
          <div className="absolute inset-0 flex items-center justify-center">
            <m.div
              animate={{ opacity: allActive ? 1 : 0.3 }}
              className="rounded-chip border border-accent-violet/40 bg-bg-elevated/90 px-4 py-2 text-center"
            >
              <p className="font-mono text-xs text-accent-violet">
                {CONTEXT_SNAPSHOT.zone}
              </p>
              <p className="font-mono text-[10px] text-text-muted">
                ctx-{CONTEXT_SNAPSHOT.context_id.slice(4)}
              </p>
            </m.div>
          </div>
        </div>

        {/* Timeline scrub */}
        <div className="relative mt-4">
          <label
            htmlFor="context-scrub"
            className="mb-2 block font-mono text-[10px] text-text-muted"
          >
            Timeline — last 30 min
          </label>
          <input
            id="context-scrub"
            type="range"
            min="0"
            max="100"
            value={scrub}
            onChange={(e) => setScrub(Number(e.target.value))}
            className="w-full accent-accent-violet"
            aria-valuetext={`${scrub}% through timeline`}
          />
        </div>

        {/* Snapshot data */}
        <m.div
          className="relative mt-4 grid grid-cols-2 gap-3"
          animate={{ opacity: allActive || activeLayers.length > 0 ? 1 : 0.5 }}
        >
          <Metric label="Workers" value={String(CONTEXT_SNAPSHOT.workers)} />
          <Metric
            label="Equipment"
            value={String(CONTEXT_SNAPSHOT.equipment_running)}
          />
          <div className="col-span-2 space-y-1">
            <p className="font-mono text-[10px] text-text-muted">Permits</p>
            <div className="flex flex-wrap gap-1">
              {CONTEXT_SNAPSHOT.active_permits.map((p) => (
                <Chip key={p} active>
                  {p}
                </Chip>
              ))}
            </div>
          </div>
          <div className="col-span-2 space-y-1">
            <p className="font-mono text-[10px] text-text-muted">Hazards</p>
            {CONTEXT_SNAPSHOT.hazards.map((h) => (
              <Badge key={h} level="warning">
                {h}
              </Badge>
            ))}
          </div>
        </m.div>
      </Panel>
    </div>
  );
}
