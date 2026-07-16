"use client";

import { m, AnimatePresence } from "framer-motion";
import { Play, RotateCcw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { cn } from "@/lib/utils/cn";

const STAGES = [
  {
    id: "event",
    label: "Event Storm",
    detail: "GAS_SENSOR ingested · external_event_id claimed",
  },
  {
    id: "twin",
    label: "Digital Twin",
    detail: "Zone Battery_A · Sensor 07 → ALERT (v16)",
  },
  {
    id: "context",
    label: "Context",
    detail: "3 workers · HOT_WORK + CONFINED_SPACE active",
  },
  {
    id: "risk",
    label: "Risk Engine",
    detail: "Score 87 CRITICAL · hot_work_plus_gas matched",
  },
  {
    id: "action",
    label: "Action",
    detail: "SUSPEND_PERMIT + NOTIFY_SUPERVISOR queued",
  },
] as const;

/**
 * Client-side interactive pipeline demo — no backend required.
 * Simulates an event flowing Events → Twin → Context → Risk → Action.
 */
export function PipelineSimulator({ className }: { className?: string }) {
  const reduced = useReducedMotion();
  const [activeIndex, setActiveIndex] = useState(-1);
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);

  const reset = useCallback(() => {
    setActiveIndex(-1);
    setRunning(false);
    setDone(false);
  }, []);

  const start = useCallback(() => {
    setActiveIndex(0);
    setRunning(true);
    setDone(false);
  }, []);

  useEffect(() => {
    if (!running || activeIndex < 0) return;
    if (activeIndex >= STAGES.length - 1) {
      const t = setTimeout(() => {
        setRunning(false);
        setDone(true);
      }, reduced ? 200 : 900);
      return () => clearTimeout(t);
    }
    const t = setTimeout(
      () => setActiveIndex((i) => i + 1),
      reduced ? 250 : 1100,
    );
    return () => clearTimeout(t);
  }, [running, activeIndex, reduced]);

  return (
    <Panel
      active
      glow={done ? "critical" : "cyan"}
      className={cn("relative overflow-hidden p-4 md:p-5", className)}
    >
      <BlueprintOverlay patternId="sim-grid" />

      <div className="relative mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">
            Interactive demo
          </p>
          <p className="mt-1 text-sm text-text-secondary">
            Inject a gas-sensor event and watch it propagate through the
            pipeline.
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={start}
            disabled={running}
            aria-label="Simulate gas sensor event through the ARGUS pipeline"
          >
            <Play className="h-3.5 w-3.5" aria-hidden />
            {running ? "Running…" : "Simulate event"}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={reset}
            disabled={running}
            aria-label="Reset pipeline simulation"
          >
            <RotateCcw className="h-3.5 w-3.5" aria-hidden />
            Reset
          </Button>
        </div>
      </div>

      <ol className="relative space-y-2" aria-live="polite">
        {STAGES.map((stage, i) => {
          const reached = i <= activeIndex;
          const current = i === activeIndex && running;
          return (
            <m.li
              key={stage.id}
              animate={{
                opacity: activeIndex < 0 ? 0.45 : reached ? 1 : 0.35,
                x: current && !reduced ? [0, 4, 0] : 0,
              }}
              transition={{ duration: 0.35 }}
              className={cn(
                "flex items-start gap-3 rounded-chip border px-3 py-2.5",
                current && "border-accent-cyan/40 bg-accent-cyan/10",
                reached && !current && "border-border-subtle bg-bg-surface/70",
                !reached && "border-border-subtle/50 bg-transparent",
              )}
            >
              <span
                className={cn(
                  "mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full font-mono text-[10px]",
                  reached
                    ? "bg-accent-cyan/20 text-accent-cyan"
                    : "bg-bg-surface text-text-muted",
                )}
              >
                {i + 1}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs text-text-primary">
                    {stage.label}
                  </span>
                  {current ? <Chip active>processing</Chip> : null}
                  {reached && !current ? (
                    <Badge level="safe" hideIcon={false}>
                      done
                    </Badge>
                  ) : null}
                </div>
                <AnimatePresence>
                  {reached ? (
                    <m.p
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-1 font-mono text-[10px] text-text-muted"
                    >
                      {stage.detail}
                    </m.p>
                  ) : null}
                </AnimatePresence>
              </div>
            </m.li>
          );
        })}
      </ol>

      {done ? (
        <p className="relative mt-4 font-mono text-xs text-signal-critical">
          Pipeline complete — CRITICAL risk assessed · actions queued to outbox
        </p>
      ) : null}
    </Panel>
  );
}
