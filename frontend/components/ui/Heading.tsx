import { cn } from "@/lib/utils/cn";

type HeadingLevel = "h1" | "h2" | "h3" | "h4";

const levelStyles: Record<HeadingLevel, string> = {
  h1: "font-display text-display-1 tracking-tight text-text-primary",
  /* Uniform section headline scale — matches featured / premium treatment */
  h2: "font-display text-display-2 tracking-tight text-text-primary md:text-[clamp(1.875rem,3.4vw,2.75rem)]",
  h3: "font-display text-display-3 tracking-tight text-text-primary",
  h4: "font-display text-lg font-semibold text-text-primary",
};

export interface HeadingProps extends React.HTMLAttributes<HTMLHeadingElement> {
  as?: HeadingLevel;
  eyebrow?: string;
  mono?: boolean;
}

export function Heading({
  as: Tag = "h2",
  eyebrow,
  mono = false,
  className,
  children,
  ...props
}: HeadingProps) {
  return (
    <div className={cn("space-y-4", className)}>
      {eyebrow ? (
        <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-accent-cyan">
          {eyebrow}
        </p>
      ) : null}
      <Tag className={cn(levelStyles[Tag], mono && "font-mono")} {...props}>
        {children}
      </Tag>
    </div>
  );
}
