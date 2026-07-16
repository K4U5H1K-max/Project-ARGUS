import { cn } from "@/lib/utils/cn";

export interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "default" | "wide" | "narrow";
}

const sizeStyles = {
  default: "max-w-content",
  wide: "max-w-wide",
  narrow: "max-w-narrow",
};

export function Container({
  size = "default",
  className,
  children,
  ...props
}: ContainerProps) {
  return (
    <div
      className={cn("mx-auto w-full px-6 md:px-8", sizeStyles[size], className)}
      {...props}
    >
      {children}
    </div>
  );
}
