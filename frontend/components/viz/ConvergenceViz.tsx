"use client";

import { m } from "framer-motion";
import {
  AlertTriangle,
  Camera,
  ClipboardCheck,
  Cpu,
  Radio,
  Users,
} from "lucide-react";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { CHALLENGE_SIGNALS } from "@/lib/content/story";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { cn } from "@/lib/utils/cn";

const iconMap = {
  sensor: Radio,
  vision: Camera,
  worker: Users,
  equipment: Cpu,
  permit: ClipboardCheck,
  incident: AlertTriangle,
} as const;

/** Fragmented signals converging into unified platform. */
export function ConvergenceViz({ className }: { className?: string }) {
  const reduced = useReducedMotion();

  const nodePositions = [
    { x: 40, y: 50 },
    { x: 200, y: 30 },
    { x: 320, y: 70 },
    { x: 60, y: 180 },
    { x: 280, y: 200 },
    { x: 180, y: 240 },
  ];

  return (
    <div className={cn("relative w-full", className)}>
      <Panel className="relative overflow-hidden p-4 md:p-6">
        <BlueprintOverlay patternId="challenge-grid" />

        <svg
          viewBox="0 0 360 280"
          className="relative h-56 w-full md:h-64"
          aria-label="Fragmented industrial signals converging into ARGUS"
          role="img"
        >
          {/* Fragmented connections */}
          {nodePositions.map((pos, i) => (
            <m.line
              key={`line-${i}`}
              x1={pos.x}
              y1={pos.y}
              x2={180}
              y2={140}
              stroke="currentColor"
              strokeWidth="1"
              className="text-accent-cyan/20"
              strokeDasharray="3 5"
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{
                delay: reduced ? 0 : 0.3 + i * 0.1,
                duration: 0.8,
              }}
            />
          ))}

          {/* Central convergence hub */}
          <m.circle
            cx="180"
            cy="140"
            r="28"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            className="text-accent-cyan"
            initial={{ scale: 0, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.8, type: "spring", stiffness: 200 }}
          />
          <m.circle
            cx="180"
            cy="140"
            r="8"
            className="fill-accent-cyan"
            initial={{ scale: 0 }}
            whileInView={{ scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1, type: "spring" }}
          />
          <text
            x="180"
            y="144"
            textAnchor="middle"
            className="fill-bg-base font-mono text-[8px] font-bold"
          >
            ARGUS
          </text>

          {/* Floating signal nodes */}
          {CHALLENGE_SIGNALS.map((signal, i) => {
            const pos = nodePositions[i];
            const Icon = iconMap[signal.icon];
            return (
              <m.g
                key={signal.label}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: reduced ? 0 : i * 0.12 }}
              >
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="16"
                  className="fill-bg-surface stroke-border-subtle"
                  strokeWidth="1"
                />
                <foreignObject x={pos.x - 8} y={pos.y - 8} width="16" height="16">
                  <Icon className="h-4 w-4 text-text-secondary" aria-hidden />
                </foreignObject>
              </m.g>
            );
          })}
        </svg>

        <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3">
          {CHALLENGE_SIGNALS.map((signal) => (
            <span
              key={signal.label}
              className="rounded-chip border border-border-subtle bg-bg-surface/60 px-2 py-1.5 text-center font-mono text-[10px] text-text-muted"
            >
              {signal.label}
            </span>
          ))}
        </div>
      </Panel>
    </div>
  );
}
