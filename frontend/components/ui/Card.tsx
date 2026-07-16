import { cn } from "@/lib/utils/cn";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  elevated?: boolean;
}

/** Base surface card — lighter than Panel, for grouped content. */
export function Card({
  elevated = false,
  className,
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        "rounded-panel border border-border-subtle bg-bg-surface/80 backdrop-blur-sm",
        elevated ? "shadow-elevation-2" : "shadow-elevation-1",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
