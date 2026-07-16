import { cn } from "@/lib/utils/cn";

export interface DividerProps extends React.HTMLAttributes<HTMLHRElement> {
  variant?: "default" | "blueprint";
}

export function Divider({
  variant = "default",
  className,
  ...props
}: DividerProps) {
  return (
    <hr
      className={cn(
        "border-0",
        variant === "default" && "h-px w-full bg-border-subtle",
        variant === "blueprint" &&
          "h-px w-full bg-gradient-to-r from-transparent via-accent-cyan/30 to-transparent",
        className,
      )}
      {...props}
    />
  );
}
