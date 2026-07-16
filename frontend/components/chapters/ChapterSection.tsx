import { Reveal } from "@/components/motion/Reveal";
import { Container } from "@/components/ui/Container";
import { Heading } from "@/components/ui/Heading";
import { Section } from "@/components/ui/Section";
import { cn } from "@/lib/utils/cn";

import { SectionConnector } from "./SectionConnector";

export interface ChapterSectionProps {
  id: string;
  eyebrow: string;
  title: string;
  description: string;
  visual: React.ReactNode;
  /** Alternate visual to the right on desktop */
  reverse?: boolean;
  /** Show pipeline connector above section */
  connector?: boolean;
  /** Scroll rhythm */
  spacing?: "featured" | "chapter" | "compact";
  children?: React.ReactNode;
  className?: string;
}

/**
 * Shared narrative chapter layout — copy + visual in consistent grid.
 * All section headlines use the same Heading scale for type hierarchy.
 */
export function ChapterSection({
  id,
  eyebrow,
  title,
  description,
  visual,
  reverse = false,
  connector = true,
  spacing = "chapter",
  children,
  className,
}: ChapterSectionProps) {
  return (
    <Section id={id} spacing={spacing} className={className}>
      {connector ? <SectionConnector /> : null}
      <Container>
        <div
          className={cn(
            "grid items-center gap-10 lg:grid-cols-2 lg:gap-16 xl:gap-20",
            reverse &&
              "lg:[&>*:first-child]:order-2 lg:[&>*:last-child]:order-1",
            spacing === "featured" && "gap-12 lg:gap-20",
          )}
        >
          <div className="space-y-6">
            <Reveal>
              <Heading as="h2" eyebrow={eyebrow}>
                {title}
              </Heading>
            </Reveal>
            <Reveal delay={0.08}>
              <p className="max-w-lg text-base leading-relaxed text-text-secondary md:text-lg md:leading-relaxed">
                {description}
              </p>
            </Reveal>
            {children ? <Reveal delay={0.12}>{children}</Reveal> : null}
          </div>
          <Reveal delay={0.16} className="w-full">
            {visual}
          </Reveal>
        </div>
      </Container>
    </Section>
  );
}
