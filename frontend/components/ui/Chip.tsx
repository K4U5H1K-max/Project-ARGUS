import { cn } from "@/lib/utils/cn";

export interface ChipProps extends React.HTMLAttributes<HTMLSpanElement> {
  active?: boolean;
}

export function Chip({
  active = false,
  className,
  children,
  ...props
}: ChipProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-chip border px-3 py-1 text-xs font-mono",
        active
          ? "border-accent-cyan/40 bg-accent-cyan/10 text-accent-cyan"
          : "border-border-subtle bg-bg-surface/60 text-text-secondary",
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
