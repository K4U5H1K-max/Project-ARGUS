"use client";

import { m } from "framer-motion";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { transitionBase } from "@/lib/animations/variants";
import { cn } from "@/lib/utils/cn";

export interface SectionConnectorProps {
  className?: string;
}

/**
 * Animated pipeline connector between narrative chapters.
 * Blueprint-inspired vertical spine with subtle horizontal rails.
 */
export function SectionConnector({ className }: SectionConnectorProps) {
  const reduced = useReducedMotion();

  return (
    <div
      className={cn(
        "relative mx-auto flex max-w-content flex-col items-center px-6 py-5 md:py-7",
        className,
      )}
      aria-hidden
    >
      {/* Horizontal blueprint rails */}
      <div className="mb-3 flex w-full max-w-xs items-center gap-3 opacity-40">
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-accent-cyan/40 to-transparent" />
        <div className="h-1 w-1 rounded-full bg-accent-cyan/50" />
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-accent-cyan/40 to-transparent" />
      </div>

      <svg
        width="24"
        height="72"
        viewBox="0 0 24 72"
        className="overflow-visible"
      >
        <m.line
          x1="12"
          y1="0"
          x2="12"
          y2="72"
          stroke="currentColor"
          strokeWidth="1"
          className="text-accent-cyan/35"
          strokeDasharray="3 5"
          initial={{ pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={
            reduced ? { duration: 0 } : { ...transitionBase, duration: 0.9 }
          }
        />
        {/* Tick marks */}
        {[18, 36, 54].map((y) => (
          <line
            key={y}
            x1="8"
            y1={y}
            x2="16"
            y2={y}
            stroke="currentColor"
            strokeWidth="0.75"
            className="text-accent-cyan/25"
          />
        ))}
        <m.circle
          cx="12"
          cy="36"
          r="3.5"
          className="fill-accent-cyan"
          animate={reduced ? undefined : { cy: [10, 62, 10] }}
          transition={
            reduced
              ? undefined
              : { duration: 4.5, repeat: Infinity, ease: "easeInOut" }
          }
        />
        <m.circle
          cx="12"
          cy="36"
          r="6"
          fill="none"
          stroke="currentColor"
          strokeWidth="0.75"
          className="text-accent-cyan/30"
          animate={
            reduced
              ? undefined
              : { cy: [10, 62, 10], opacity: [0.5, 0.2, 0.5] }
          }
          transition={
            reduced
              ? undefined
              : { duration: 4.5, repeat: Infinity, ease: "easeInOut" }
          }
        />
      </svg>

      <div className="mt-3 flex w-full max-w-xs items-center gap-3 opacity-30">
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-accent-violet/35 to-transparent" />
      </div>
    </div>
  );
}
