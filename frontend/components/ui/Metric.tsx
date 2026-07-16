import { cn } from "@/lib/utils/cn";

export interface MetricProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: string;
  unit?: string;
  trend?: "up" | "down" | "neutral";
}

export function Metric({
  label,
  value,
  unit,
  trend = "neutral",
  className,
  ...props
}: MetricProps) {
  return (
    <div className={cn("space-y-1", className)} {...props}>
      <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
        {label}
      </p>
      <p className="flex items-baseline gap-1 font-mono text-xl font-medium text-text-primary md:text-2xl">
        <span>{value}</span>
        {unit ? (
          <span className="text-sm text-text-secondary">{unit}</span>
        ) : null}
        {trend !== "neutral" ? (
          <span
            className={cn(
              "text-xs",
              trend === "up" ? "text-signal-warning" : "text-signal-safe",
            )}
            aria-hidden
          >
            {trend === "up" ? "↑" : "↓"}
          </span>
        ) : null}
      </p>
    </div>
  );
}
