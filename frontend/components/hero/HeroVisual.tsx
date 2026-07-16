"use client";

import { m } from "framer-motion";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { Panel } from "@/components/ui/Panel";
import { Chip } from "@/components/ui/Chip";
import { Metric } from "@/components/ui/Metric";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/utils/cn";

const EVENTS = [
  { type: "GAS_SENSOR", severity: "warning" },
  { type: "HOT_WORK", severity: "info" },
  { type: "ENTRY", severity: "info" },
  { type: "PPE_VIOLATION", severity: "critical" },
] as const;

const severityLevel = {
  info: "info",
  warning: "warning",
  critical: "critical",
} as const;

const TWIN_EDGES = [
  ["120", "100", "80", "130"],
  ["120", "100", "160", "130"],
  ["80", "130", "60", "170"],
  ["160", "130", "180", "170"],
  ["120", "100", "120", "60"],
  ["80", "130", "120", "100"],
  ["160", "130", "200", "100"],
] as const;

/**
 * Custom command-center visualization — event stream, digital twin graph,
 * and risk assessment panel. SVG-based, subtly animated.
 */
export function HeroVisual({ className }: { className?: string }) {
  const reduced = useReducedMotion();

  const drawTransition = reduced
    ? { duration: 0 }
    : { duration: 1.1, ease: [0.2, 0, 0, 1] as const };

  return (
    <div className={cn("relative w-full", className)}>
      {/* Layered ambient glow */}
      <div
        className="absolute -inset-4 rounded-panel bg-accent-cyan/[0.06] blur-3xl animate-pulse-glow"
        aria-hidden
      />
      <div
        className="absolute -right-6 top-1/4 h-1/2 w-1/3 rounded-full bg-accent-violet/[0.08] blur-2xl animate-gradient-shift"
        aria-hidden
      />

      <Panel
        active
        glow="cyan"
        className="relative overflow-hidden p-4 md:p-6 lg:p-7"
      >
        {/* Blueprint overlay */}
        <svg
          className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.07]"
          aria-hidden
        >
          <defs>
            <pattern
              id="hero-grid"
              width="24"
              height="24"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M24 0 L0 0 0 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="0.5"
                className="text-accent-cyan"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#hero-grid)" />
        </svg>

        {/* Blueprint scan sweep */}
        {!reduced ? (
          <div
            className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent-cyan/50 to-transparent animate-scan-line"
            style={{ animationDuration: "10s" }}
            aria-hidden
          />
        ) : null}

        <div className="relative grid gap-5 lg:grid-cols-3 lg:gap-4">
          {/* ── Event stream panel ── */}
          <m.div
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.15, ...drawTransition }}
            className="space-y-3"
          >
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">
              Event Stream
            </p>
            <div className="space-y-2">
              {EVENTS.map((evt, i) => (
                <m.div
                  key={evt.type}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{
                    delay: reduced ? 0 : 0.35 + i * 0.12,
                    duration: 0.35,
                    ease: [0.2, 0, 0, 1],
                  }}
                  className="flex items-center justify-between rounded-chip border border-border-subtle bg-bg-surface/80 px-3 py-2"
                >
                  <Chip active={i === 0}>{evt.type}</Chip>
                  <Badge level={severityLevel[evt.severity]}>
                    {evt.severity}
                  </Badge>
                </m.div>
              ))}
            </div>
            {/* Dual pipeline flow */}
            <svg
              viewBox="0 0 200 40"
              className="h-10 w-full text-accent-cyan/40"
              aria-hidden
            >
              <m.path
                d="M0 14 H200"
                fill="none"
                stroke="currentColor"
                strokeWidth="1"
                strokeDasharray="4 4"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 0.7, duration: 1.4, ease: "easeInOut" }}
              />
              <m.path
                d="M0 26 H200"
                fill="none"
                stroke="currentColor"
                strokeWidth="0.75"
                className="text-accent-violet/30"
                strokeDasharray="3 5"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 0.9, duration: 1.4, ease: "easeInOut" }}
              />
              <m.circle
                cx="20"
                cy="14"
                r="2.5"
                fill="currentColor"
                className="text-accent-cyan"
                animate={reduced ? undefined : { cx: [10, 190, 10] }}
                transition={
                  reduced
                    ? undefined
                    : { duration: 5.5, repeat: Infinity, ease: "linear" }
                }
              />
              <m.circle
                cx="40"
                cy="26"
                r="2"
                fill="currentColor"
                className="text-accent-violet"
                animate={reduced ? undefined : { cx: [190, 10, 190] }}
                transition={
                  reduced
                    ? undefined
                    : { duration: 7, repeat: Infinity, ease: "linear" }
                }
              />
            </svg>
          </m.div>

          {/* ── Digital twin / graph panel ── */}
          <m.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.35, ...drawTransition }}
            className="relative flex flex-col items-center"
          >
            <p className="mb-2 self-start font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">
              Digital Twin
            </p>
            <svg
              viewBox="0 0 240 200"
              className="h-48 w-full max-w-[260px] md:h-52"
              aria-label="Digital twin topology graph"
              role="img"
            >
              {/* Soft zone fill */}
              <m.polygon
                points="120,30 200,80 200,160 40,160 40,80"
                fill="currentColor"
                className="text-accent-cyan/[0.04]"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5, duration: 0.8 }}
              />

              {/* Zone polygon */}
              <m.polygon
                points="120,30 200,80 200,160 40,160 40,80"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.25"
                className="text-accent-cyan/55"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ delay: 0.5, duration: 1 }}
              />

              {/* Graph edges */}
              {TWIN_EDGES.map(([x1, y1, x2, y2], i) => (
                <m.line
                  key={i}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-accent-violet/45"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 1 }}
                  transition={{ delay: 0.7 + i * 0.08, duration: 0.45 }}
                />
              ))}

              {/* Extra telemetry nodes */}
              <circle cx="200" cy="100" r="3.5" className="fill-accent-violet/70" />
              <circle cx="100" cy="150" r="3" className="fill-signal-info/80" />

              {/* Core nodes */}
              <m.circle
                cx="120"
                cy="100"
                r="8"
                className="fill-accent-cyan"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.9, type: "spring", stiffness: 220 }}
              />
              <circle
                cx="80"
                cy="130"
                r="5"
                className="fill-bg-surface stroke-accent-cyan"
                strokeWidth="1.25"
              />
              <circle
                cx="160"
                cy="130"
                r="5"
                className="fill-bg-surface stroke-accent-cyan"
                strokeWidth="1.25"
              />
              <circle cx="120" cy="60" r="4" className="fill-signal-info" />
              <circle cx="60" cy="170" r="4" className="fill-signal-warning" />
              <circle cx="180" cy="170" r="4" className="fill-signal-safe" />

              {/* Multi sensor pulses */}
              <m.circle
                cx="120"
                cy="60"
                r="4"
                fill="none"
                stroke="currentColor"
                strokeWidth="1"
                className="text-signal-info"
                animate={
                  reduced
                    ? undefined
                    : { r: [4, 14, 4], opacity: [0.8, 0, 0.8] }
                }
                transition={
                  reduced
                    ? undefined
                    : { duration: 2.8, repeat: Infinity, ease: "easeInOut" }
                }
              />
              <m.circle
                cx="60"
                cy="170"
                r="4"
                fill="none"
                stroke="currentColor"
                strokeWidth="1"
                className="text-signal-warning"
                animate={
                  reduced
                    ? undefined
                    : { r: [4, 11, 4], opacity: [0.7, 0, 0.7] }
                }
                transition={
                  reduced
                    ? undefined
                    : {
                        duration: 3.2,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: 0.8,
                      }
                }
              />
              <m.circle
                cx="200"
                cy="100"
                r="3"
                fill="none"
                stroke="currentColor"
                strokeWidth="1"
                className="text-accent-violet"
                animate={
                  reduced
                    ? undefined
                    : { r: [3, 10, 3], opacity: [0.6, 0, 0.6] }
                }
                transition={
                  reduced
                    ? undefined
                    : {
                        duration: 3.5,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: 1.2,
                      }
                }
              />

              {/* Flow particle along edge */}
              {!reduced ? (
                <m.circle
                  r="2"
                  className="fill-accent-cyan"
                  animate={{
                    cx: [120, 80, 60, 80, 120],
                    cy: [100, 130, 170, 130, 100],
                  }}
                  transition={{
                    duration: 8,
                    repeat: Infinity,
                    ease: "linear",
                  }}
                />
              ) : null}
            </svg>
            <p className="mt-1 font-mono text-[10px] text-text-muted">
              Zone Battery_A · v12
            </p>
          </m.div>

          {/* ── Risk assessment panel ── */}
          <m.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5, ...drawTransition }}
            className="space-y-3"
          >
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">
              Risk Assessment
            </p>
            <div className="rounded-chip border border-signal-critical/30 bg-signal-critical/5 p-3.5 shadow-glow-critical/50">
              <div className="mb-3 flex items-center justify-between">
                <Badge level="critical">CRITICAL</Badge>
                <span className="font-mono text-xs text-text-muted">
                  92% conf
                </span>
              </div>
              <Metric label="Risk Score" value="87" unit="/100" trend="up" />
              <p className="mt-3 text-xs leading-relaxed text-text-secondary">
                Hot work + elevated gas detected in adjacent zone. Worker
                density exceeds threshold.
              </p>
            </div>

            {/* Heat bloom SVG */}
            <svg viewBox="0 0 200 60" className="h-14 w-full" aria-hidden>
              <defs>
                <radialGradient id="heat-bloom">
                  <stop
                    offset="0%"
                    stopColor="var(--signal-critical)"
                    stopOpacity="0.55"
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
                cy="30"
                rx="20"
                ry="15"
                fill="url(#heat-bloom)"
                initial={{ rx: 0, ry: 0, opacity: 0 }}
                animate={{ rx: 55, ry: 26, opacity: 1 }}
                transition={{ delay: 1.1, duration: 1.1, ease: [0.2, 0, 0, 1] }}
              />
              <m.circle
                cx="100"
                cy="30"
                r="4"
                className="fill-signal-critical"
                animate={reduced ? undefined : { opacity: [1, 0.45, 1] }}
                transition={
                  reduced ? undefined : { duration: 2.2, repeat: Infinity }
                }
              />
            </svg>
          </m.div>
        </div>

        {/* Bottom pipeline label */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-x-2 gap-y-1 border-t border-border-subtle pt-4">
          {["Events", "Twin", "Context", "Risk", "Actions"].map((step, i) => (
            <m.span
              key={step}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.25 + i * 0.08 }}
              className="flex items-center gap-2"
            >
              <span className="font-mono text-[10px] tracking-wide text-text-muted">
                {step}
              </span>
              {i < 4 ? (
                <span className="text-accent-cyan/45" aria-hidden>
                  →
                </span>
              ) : null}
            </m.span>
          ))}
        </div>
      </Panel>
    </div>
  );
}
