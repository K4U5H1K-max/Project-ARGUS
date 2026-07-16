import { cn } from "@/lib/utils/cn";

export interface DataSourceBadgeProps {
  isLive: boolean;
  isLoading?: boolean;
  className?: string;
}

/** Indicates whether section data is live or sample fallback. */
export function DataSourceBadge({
  isLive,
  isLoading = false,
  className,
}: DataSourceBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider",
        isLoading && "border-border-subtle text-text-muted",
        !isLoading && isLive && "border-signal-safe/30 bg-signal-safe/10 text-signal-safe",
        !isLoading && !isLive && "border-signal-warning/30 bg-signal-warning/10 text-signal-warning",
        className,
      )}
      aria-live="polite"
    >
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          isLoading && "bg-text-muted animate-pulse",
          !isLoading && isLive && "bg-signal-safe",
          !isLoading && !isLive && "bg-signal-warning",
        )}
        aria-hidden
      />
      {isLoading ? "Connecting" : isLive ? "Live" : "Sample data"}
    </span>
  );
}
