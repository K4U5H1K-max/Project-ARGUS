import { cn } from "@/lib/utils/cn";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "block" | "circle";
}

/** Loading skeleton aligned with design system surfaces. */
export function Skeleton({
  variant = "block",
  className,
  ...props
}: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-chip bg-bg-surface/80",
        variant === "text" && "h-3 w-full",
        variant === "block" && "h-16 w-full",
        variant === "circle" && "h-8 w-8 rounded-full",
        className,
      )}
      aria-hidden
      {...props}
    />
  );
}
