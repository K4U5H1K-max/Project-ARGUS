import { ArrowRight, Layers } from "lucide-react";

import { ScrollIndicator } from "@/components/common/ScrollIndicator";
import { Reveal } from "@/components/motion/Reveal";
import { Button } from "@/components/ui/Button";
import { Container } from "@/components/ui/Container";
import { Section } from "@/components/ui/Section";
import { HeroVisual } from "@/components/hero/HeroVisual";
import { TrustIndicators } from "@/components/hero/TrustIndicators";

export function HeroSection() {
  return (
    <Section
      id="home"
      spacing="hero"
      className="relative flex min-h-[100svh] flex-col justify-center pt-20 md:pt-24"
    >
      <div
        className="pointer-events-none absolute inset-0 -z-10 overflow-hidden"
        aria-hidden
      >
        <div className="absolute left-1/2 top-1/4 h-[40vh] w-[70vw] -translate-x-1/2 rounded-full bg-accent-cyan/[0.07] blur-[100px] animate-pulse-glow" />
        <div className="absolute bottom-1/4 right-0 h-[30vh] w-[40vw] rounded-full bg-accent-violet/[0.06] blur-[90px] animate-gradient-shift" />
      </div>

      <Container className="relative flex flex-1 flex-col justify-center">
        <div className="grid items-center gap-14 lg:grid-cols-[1.05fr_1.15fr] lg:gap-12 xl:gap-16">
          <div className="flex flex-col items-center text-center lg:items-start lg:text-left">
            <Reveal>
              <p className="mb-5 font-mono text-[11px] uppercase tracking-[0.28em] text-accent-cyan">
                Industrial Safety Intelligence
              </p>
            </Reveal>

            <Reveal delay={0.08}>
              <h1 className="font-display text-display-1 text-text-primary">
                Industrial events.
                <br />
                <span className="text-accent-cyan">Intelligent decisions.</span>
              </h1>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="mt-7 max-w-xl text-[1.05rem] leading-[1.7] text-text-secondary md:text-lg md:leading-[1.75]">
                ARGUS is an AI-powered industrial safety platform that
                transforms raw operational events into intelligent, real-time
                decisions through Digital Twins, Knowledge Graphs, and
                Predictive Risk Analysis.
              </p>
            </Reveal>

            {/* Plain flex — no Stagger wrappers (avoids motion layout quirks) */}
            <div className="mt-9 flex w-full flex-col items-center gap-3 sm:flex-row sm:justify-center lg:justify-start">
              <Button
                href="#challenge"
                size="lg"
                className="w-full shadow-glow-cyan sm:w-auto"
              >
                Watch the system think
                <ArrowRight className="h-4 w-4" aria-hidden />
              </Button>
              <Button
                href="#pipeline"
                variant="secondary"
                size="lg"
                className="w-full sm:w-auto"
              >
                <Layers className="h-4 w-4" aria-hidden />
                Explore the architecture
              </Button>
            </div>

            <div className="mt-10 w-full border-t border-border-subtle/60 pt-6">
              <TrustIndicators />
            </div>
          </div>

          <Reveal delay={0.22} className="w-full lg:origin-center lg:scale-[1.02]">
            <HeroVisual />
          </Reveal>
        </div>

        <div className="mt-14 flex justify-center pb-4 lg:mt-16">
          <ScrollIndicator targetId="challenge" />
        </div>
      </Container>
    </Section>
  );
}
