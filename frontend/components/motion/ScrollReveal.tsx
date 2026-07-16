"use client";

import { m, type HTMLMotionProps } from "framer-motion";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import {
  reducedMotionVariants,
  revealVariants,
} from "@/lib/animations/variants";

export interface ScrollRevealProps extends HTMLMotionProps<"div"> {
  delay?: number;
}

/** Reveals content when scrolled into the viewport. */
export function ScrollReveal({
  children,
  className,
  delay = 0,
  ...props
}: ScrollRevealProps) {
  const reduced = useReducedMotion();
  const variants = reduced ? reducedMotionVariants : revealVariants;

  return (
    <m.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.2 }}
      variants={variants}
      transition={{ delay }}
      className={className}
      {...props}
    >
      {children}
    </m.div>
  );
}
