import { cn } from "@/lib/utils/cn";

export interface LogoProps {
  className?: string;
  showWordmark?: boolean;
}

/** Temporary ARGUS logo — graph ring + crosshair mark. */
export function Logo({ className, showWordmark = true }: LogoProps) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <svg
        width="32"
        height="32"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden
        className="shrink-0"
      >
        <circle
          cx="16"
          cy="16"
          r="13"
          stroke="currentColor"
          strokeWidth="1"
          className="text-accent-cyan/40"
        />
        <circle
          cx="16"
          cy="16"
          r="7"
          stroke="currentColor"
          strokeWidth="1"
          strokeDasharray="3 3"
          className="text-accent-violet/50"
        />
        <circle cx="16" cy="16" r="2.5" fill="currentColor" className="text-accent-cyan" />
        <line x1="16" y1="3" x2="16" y2="9" stroke="currentColor" strokeWidth="1" className="text-accent-cyan/60" />
        <line x1="16" y1="23" x2="16" y2="29" stroke="currentColor" strokeWidth="1" className="text-accent-cyan/60" />
        <line x1="3" y1="16" x2="9" y2="16" stroke="currentColor" strokeWidth="1" className="text-accent-cyan/60" />
        <line x1="23" y1="16" x2="29" y2="16" stroke="currentColor" strokeWidth="1" className="text-accent-cyan/60" />
      </svg>
      {showWordmark ? (
        <span className="font-display text-lg font-semibold tracking-tight text-text-primary">
          ARGUS
        </span>
      ) : null}
    </div>
  );
}
