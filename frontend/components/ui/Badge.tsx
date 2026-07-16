import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";

import { cn } from "@/lib/utils/cn";
import type { SignalLevel } from "@/types";

const levelStyles: Record<SignalLevel, string> = {
  info: "bg-signal-info/15 text-signal-info border-signal-info/30",
  warning: "bg-signal-warning/15 text-signal-warning border-signal-warning/30",
  critical: "bg-signal-critical/15 text-signal-critical border-signal-critical/30",
  safe: "bg-signal-safe/15 text-signal-safe border-signal-safe/30",
};

const levelIcons: Record<SignalLevel, typeof Info> = {
  info: Info,
  warning: AlertTriangle,
  critical: AlertCircle,
  safe: CheckCircle2,
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  level?: SignalLevel;
  /** Hide status icon (rare — default shows icon for a11y) */
  hideIcon?: boolean;
}

export function Badge({
  level = "info",
  hideIcon = false,
  className,
  children,
  ...props
}: BadgeProps) {
  const Icon = levelIcons[level];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium font-mono uppercase tracking-wider",
        levelStyles[level],
        className,
      )}
      {...props}
    >
      {!hideIcon ? (
        <Icon className="h-3 w-3 shrink-0" aria-hidden />
      ) : null}
      <span className="sr-only">{level}: </span>
      {children}
    </span>
  );
}
