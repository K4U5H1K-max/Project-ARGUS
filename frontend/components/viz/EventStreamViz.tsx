"use client";

import { m, AnimatePresence } from "framer-motion";
import { useEffect, useRef, useState } from "react";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { STORY_EVENTS, type StoryEvent } from "@/lib/content/story";
import { Badge } from "@/components/ui/Badge";
import { Chip } from "@/components/ui/Chip";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { cn } from "@/lib/utils/cn";

const severityLevel = {
  info: "info",
  warning: "warning",
  critical: "critical",
} as const;

/** Continuous event stream with duplicate fade — idempotency hint. */
const STATIC_EVENTS = STORY_EVENTS.filter((e) => !e.isDuplicate);

export function EventStreamViz({ className }: { className?: string }) {
  const reduced = useReducedMotion();
  const [visibleEvents, setVisibleEvents] = useState<StoryEvent[]>(
    reduced ? STATIC_EVENTS : [STORY_EVENTS[0]],
  );
  const streamIndexRef = useRef(0);

  useEffect(() => {
    if (reduced) return;

    const interval = setInterval(() => {
      streamIndexRef.current =
        (streamIndexRef.current + 1) % STORY_EVENTS.length;
      const event = STORY_EVENTS[streamIndexRef.current];

      setVisibleEvents((current) => {
        if (event.isDuplicate) {
          return current.map((e) =>
            e.external_event_id === event.external_event_id
              ? { ...e, isDuplicate: true }
              : e,
          );
        }
        return [...current, event].slice(-5);
      });
    }, 1800);

    return () => clearInterval(interval);
  }, [reduced]);

  return (
    <div className={cn("relative w-full", className)}>
      <Panel active glow="cyan" className="relative overflow-hidden p-4 md:p-6">
        <BlueprintOverlay patternId="event-grid" />

        <p className="relative mb-4 font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
          POST /events — Ingestion Stream
        </p>

        <div className="relative min-h-[220px] space-y-2">
          <AnimatePresence mode="popLayout">
            {visibleEvents.map((event) => (
              <m.div
                key={`${event.event_id}-${event.isDuplicate ? "dup" : "new"}`}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{
                  opacity: event.isDuplicate ? 0.35 : 1,
                  x: 0,
                  scale: event.isDuplicate ? 0.97 : 1,
                }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.4 }}
                className={cn(
                  "flex items-center justify-between rounded-chip border px-3 py-2.5",
                  event.isDuplicate
                    ? "border-border-subtle/50 bg-bg-surface/40 line-through decoration-text-muted/50"
                    : "border-border-subtle bg-bg-surface/80",
                )}
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  <Chip active={!event.isDuplicate}>{event.event_type}</Chip>
                  <span className="truncate font-mono text-[10px] text-text-muted">
                    {event.external_event_id}
                  </span>
                </div>
                <Badge level={severityLevel[event.severity]}>
                  {event.severity}
                </Badge>
              </m.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Pipeline flow into system */}
        <svg viewBox="0 0 300 32" className="mt-4 h-8 w-full" aria-hidden>
          <m.path
            d="M0 16 H300"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            className="text-accent-cyan/40"
            strokeDasharray="4 4"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.5 }}
          />
          <m.circle
            cx="0"
            cy="16"
            r="3"
            className="fill-accent-cyan"
            animate={reduced ? undefined : { cx: [0, 300, 0] }}
            transition={
              reduced
                ? undefined
                : { duration: 5, repeat: Infinity, ease: "linear" }
            }
          />
        </svg>

        <p className="mt-3 font-mono text-[10px] text-text-muted">
          Duplicate events skipped via processed_events ledger
        </p>
      </Panel>
    </div>
  );
}
