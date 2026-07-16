import { ArrowRight, BookOpen, LayoutDashboard, Mail } from "lucide-react";

import { Reveal } from "@/components/motion/Reveal";
import { Button } from "@/components/ui/Button";
import { Container } from "@/components/ui/Container";
import { Section } from "@/components/ui/Section";
import { SectionConnector } from "@/components/chapters/SectionConnector";
import { SITE } from "@/lib/theme/tokens";

export function FinalCTASection() {
  return (
    <Section id="cta" spacing="featured" className="relative pb-12 md:pb-16">
      <SectionConnector />

      <div
        className="pointer-events-none absolute inset-0 -z-10 overflow-hidden"
        aria-hidden
      >
        <div className="absolute left-1/2 top-1/2 h-[50vh] w-[80vw] -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent-cyan/[0.08] blur-[110px] animate-pulse-glow" />
        <div className="absolute bottom-0 left-1/4 h-[30vh] w-[40vw] rounded-full bg-accent-violet/[0.06] blur-[90px]" />
      </div>

      <Container>
        <div className="relative mx-auto max-w-2xl overflow-hidden rounded-panel border border-border-subtle bg-bg-elevated/50 px-6 py-12 text-center shadow-elevation-2 backdrop-blur-sm md:px-12 md:py-16">
          <div
            className="pointer-events-none absolute inset-0 opacity-[0.05]"
            aria-hidden
          >
            <svg className="h-full w-full">
              <defs>
                <pattern
                  id="cta-grid"
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
              <rect width="100%" height="100%" fill="url(#cta-grid)" />
            </svg>
          </div>

          <div className="relative">
            <Reveal>
              <p className="mb-5 font-mono text-[11px] uppercase tracking-[0.26em] text-accent-cyan">
                Enterprise Operational Intelligence
              </p>
            </Reveal>

            <Reveal delay={0.08}>
              <h2 className="font-display text-display-2 text-text-primary md:text-[clamp(2rem,3.5vw,3rem)]">
                Industrial events.
                <br />
                <span className="text-accent-cyan">Intelligent decisions.</span>
              </h2>
            </Reveal>

            <Reveal delay={0.14}>
              <p className="mx-auto mt-7 max-w-lg text-base leading-relaxed text-text-secondary md:text-lg">
                ARGUS transforms continuous operational telemetry into
                deterministic intelligence — from event ingestion through
                digital twins, explainable risk, and coordinated response.
              </p>
            </Reveal>

            {/* Plain flex — avoid motion wrappers that can leave remount artifacts */}
            <div className="mt-11 flex flex-col items-center justify-center gap-3 sm:flex-row sm:flex-wrap">
              <Button
                href={SITE.dashboard}
                size="lg"
                className="shadow-glow-cyan"
              >
                <LayoutDashboard className="h-4 w-4" aria-hidden />
                View Dashboard
              </Button>
              <Button href="#pipeline" variant="secondary" size="lg">
                Explore the architecture
                <ArrowRight className="h-4 w-4" aria-hidden />
              </Button>
              <Button href={SITE.docs} variant="secondary" size="lg">
                <BookOpen className="h-4 w-4" aria-hidden />
                Documentation
              </Button>
              <Button href="#contact" variant="ghost" size="lg">
                <Mail className="h-4 w-4" aria-hidden />
                Request a demo
              </Button>
            </div>
          </div>
        </div>
      </Container>
    </Section>
  );
}
