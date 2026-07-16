import { cn } from "@/lib/utils/cn";
import type { ButtonSize, ButtonVariant } from "@/types";

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-accent-cyan text-bg-base hover:bg-accent-cyan/90 shadow-glow-cyan border border-accent-cyan/30",
  secondary:
    "bg-transparent text-text-primary border border-border-subtle hover:border-accent-cyan/40 hover:bg-bg-surface/60",
  ghost:
    "bg-transparent text-text-secondary hover:text-text-primary hover:bg-bg-surface/50",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "h-9 px-4 text-sm gap-1.5",
  md: "h-11 px-5 text-sm gap-2",
  lg: "h-12 px-6 text-base gap-2",
};

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  asChild?: boolean;
  href?: string;
}

export function buttonClassName({
  variant = "primary",
  size = "md",
  className,
}: {
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
}) {
  return cn(
    "inline-flex items-center justify-center rounded-full font-medium transition-all duration-300",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-cyan/50 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-base",
    "disabled:pointer-events-none disabled:opacity-50",
    variantStyles[variant],
    sizeStyles[size],
    className,
  );
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  href,
  children,
  ...props
}: ButtonProps) {
  const classes = buttonClassName({ variant, size, className });

  if (href) {
    return (
      <a href={href} className={classes}>
        {children}
      </a>
    );
  }

  return (
    <button type="button" className={classes} {...props}>
      {children}
    </button>
  );
}
