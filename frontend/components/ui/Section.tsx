import { cn } from "@/lib/utils/cn";

export interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  id?: string;
  /**
   * Vertical padding scale for chapter sections.
   * - hero: first viewport, maximum breathing room
   * - featured: high-emphasis chapters (Risk, etc.)
   * - chapter: default narrative sections
   * - compact: denser supporting sections
   */
  spacing?: "hero" | "featured" | "chapter" | "compact";
}

const spacingStyles = {
  hero: "py-28 md:py-36 lg:py-44",
  featured: "py-24 md:py-32 lg:py-40",
  chapter: "py-16 md:py-24 lg:py-28",
  compact: "py-12 md:py-16",
};

export function Section({
  spacing = "chapter",
  className,
  children,
  ...props
}: SectionProps) {
  return (
    <section
      className={cn("relative w-full", spacingStyles[spacing], className)}
      {...props}
    >
      {children}
    </section>
  );
}
