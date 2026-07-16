import { cn } from "@/lib/utils/cn";

export interface BlueprintOverlayProps {
  patternId?: string;
  className?: string;
}

/** Reusable blueprint grid overlay — matches Hero visual style. */
export function BlueprintOverlay({
  patternId = "blueprint-grid",
  className,
}: BlueprintOverlayProps) {
  return (
    <svg
      className={cn(
        "pointer-events-none absolute inset-0 h-full w-full opacity-[0.06]",
        className,
      )}
      aria-hidden
    >
      <defs>
        <pattern
          id={patternId}
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
      <rect width="100%" height="100%" fill={`url(#${patternId})`} />
    </svg>
  );
}
