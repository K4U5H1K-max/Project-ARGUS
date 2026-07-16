"use client";

import { useEffect, useState } from "react";

/** Tracks vertical scroll offset for nav blur / transparency transitions. */
export function useScrollPosition(threshold = 48) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > threshold);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [threshold]);

  return scrolled;
}
