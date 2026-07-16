"use client";

import { m } from "framer-motion";
import { useEffect, useState } from "react";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { INCIDENT_LIFECYCLE } from "@/lib/content/story";
import { Badge } from "@/components/ui/Badge";
import { Chip } from "@/components/ui/Chip";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { cn } from "@/lib/utils/cn";

const WORKFLOW_STEPS = [
  { phase: "Detect", modules: ["Vision AI", "Sensors"], api: "/vision/detections" },
  { phase: "Assess", modules: ["Risk Engine", "Context"], api: "/risk/current" },
  { phase: "Resolve", modules: ["Permit", "Compliance"], api: "/permit/resolve" },
  { phase: "Respond", modules: ["Emergency", "Notifications"], api: "/emergency/incidents" },
  { phase: "Predict", modules: ["Predictive"], api: "/predictive/forecast" },
] as const;

/** Unified operational workflow across all orchestration modules. */
export function OrchestrationWorkflowViz({ className }: { className?: string }) {
  const reduced = useReducedMotion();
  const [activeStep, setActiveStep] = useState(0);
  const [incidentIndex, setIncidentIndex] = useState(0);

  useEffect(() => {
    if (reduced) return;
    const interval = setInterval(() => {
      setActiveStep((s) => (s + 1) % WORKFLOW_STEPS.length);
      setIncidentIndex((i) => Math.min(i + 1, INCIDENT_LIFECYCLE.length - 1));
    }, 2500);
    return () => clearInterval(interval);
  }, [reduced]);

  return (
    <div className={cn("relative w-full", className)}>
      <Panel className="relative overflow-hidden p-4 md:p-6">
        <BlueprintOverlay patternId="orch-grid" />

        <p className="relative mb-4 font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
          Coordinated Operations Workflow
        </p>

        {/* Workflow pipeline */}
        <div className="relative mb-6 flex flex-wrap justify-between gap-2">
          {WORKFLOW_STEPS.map((step, i) => (
            <button
              key={step.phase}
              type="button"
              onClick={() => setActiveStep(i)}
              className={cn(
                "flex-1 min-w-[80px] rounded-chip border px-2 py-2 text-center transition-all",
                activeStep === i
                  ? "border-accent-cyan/40 bg-accent-cyan/10"
                  : "border-border-subtle bg-bg-surface/40",
              )}
              aria-pressed={activeStep === i}
            >
              <p className="font-mono text-xs text-text-primary">{step.phase}</p>
              <p className="font-mono text-[9px] text-text-muted">{step.api}</p>
            </button>
          ))}
        </div>

        {/* Active step detail */}
        <m.div
          key={activeStep}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 rounded-chip border border-border-subtle bg-bg-surface/60 p-3"
        >
          <p className="font-mono text-xs text-accent-cyan">
            {WORKFLOW_STEPS[activeStep].phase}
          </p>
          <div className="mt-2 flex flex-wrap gap-1">
            {WORKFLOW_STEPS[activeStep].modules.map((mod) => (
              <Chip key={mod} active>
                {mod}
              </Chip>
            ))}
          </div>
        </m.div>

        {/* Incident lifecycle strip */}
        <p className="relative mb-2 font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
          Incident Lifecycle
        </p>
        <div className="relative flex flex-wrap gap-1">
          {INCIDENT_LIFECYCLE.map((state, i) => (
            <m.div
              key={state.status}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{
                opacity: i <= incidentIndex ? 1 : 0.3,
                scale: i === incidentIndex ? 1.05 : 1,
              }}
              className={cn(
                "rounded-chip border px-2 py-1 font-mono text-[10px]",
                i <= incidentIndex
                  ? "border-accent-cyan/30 bg-accent-cyan/5 text-accent-cyan"
                  : "border-border-subtle text-text-muted",
              )}
            >
              {state.label}
            </m.div>
          ))}
        </div>

        <div className="relative mt-4 flex items-center gap-2">
          <Badge level="warning">Permit Conflict</Badge>
          <Badge level="critical">PPE Violation</Badge>
          <Badge level="info">Notification Dispatched</Badge>
        </div>
      </Panel>
    </div>
  );
}
