"use client";

import { m } from "framer-motion";
import { ChevronDown } from "lucide-react";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import { cn } from "@/lib/utils/cn";

export interface ScrollIndicatorProps {
  targetId?: string;
  className?: string;
}

export function ScrollIndicator({
  targetId = "challenge",
  className,
}: ScrollIndicatorProps) {
  const reduced = useReducedMotion();

  return (
    <a
      href={`#${targetId}`}
      className={cn(
        "group flex flex-col items-center gap-2.5 text-text-muted transition-colors duration-300 hover:text-accent-cyan",
        className,
      )}
      aria-label="Scroll to explore the platform"
    >
      <span className="font-mono text-[10px] uppercase tracking-[0.24em]">
        Explore
      </span>
      <m.span
        animate={reduced ? undefined : { y: [0, 5, 0] }}
        transition={
          reduced
            ? undefined
            : { duration: 2.2, repeat: Infinity, ease: "easeInOut" }
        }
        className="flex h-9 w-9 items-center justify-center rounded-full border border-border-subtle bg-bg-surface/60 shadow-elevation-1 transition-colors group-hover:border-accent-cyan/40"
      >
        <ChevronDown className="h-4 w-4" aria-hidden />
      </m.span>
    </a>
  );
}
