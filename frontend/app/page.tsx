import { HeroSection } from "@/components/hero/HeroSection";
import { SampleDataDisclosure } from "@/components/common/SampleDataDisclosure";
import { StoryPipeline } from "@/components/chapters/StoryPipeline";
import { PageTransition } from "@/components/motion/PageTransition";

export default function HomePage() {
  return (
    <PageTransition>
      <HeroSection />
      <SampleDataDisclosure />
      <StoryPipeline />
    </PageTransition>
  );
}
