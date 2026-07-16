import { cn } from "@/lib/utils/cn";

export interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Adds active glow for instrument-panel emphasis */
  active?: boolean;
  glow?: "cyan" | "violet" | "critical" | "none";
}

/** Instrument panel — primary content surface for command-center UI. */
export function Panel({
  active = false,
  glow = "none",
  className,
  children,
  ...props
}: PanelProps) {
  return (
    <div
      className={cn(
        "rounded-panel border border-border-subtle bg-bg-elevated/90 backdrop-blur-md",
        "shadow-elevation-1 inner-highlight",
        active && "border-accent-cyan/30",
        glow === "cyan" && "shadow-glow-cyan",
        glow === "violet" && "shadow-glow-violet",
        glow === "critical" && "shadow-glow-critical",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
