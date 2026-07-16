"use client";

import { Fade } from "@/components/motion/Fade";

interface LiveDataFadeProps {
  children: React.ReactNode;
  isLoading?: boolean;
  skeleton: React.ReactNode;
}

/** Progressive render — skeleton first, fade to content without layout shift. */
export function LiveDataFade({
  children,
  isLoading = false,
  skeleton,
}: LiveDataFadeProps) {
  if (isLoading) {
    return <div aria-busy="true">{skeleton}</div>;
  }

  return <Fade>{children}</Fade>;
}
