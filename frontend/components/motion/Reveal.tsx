"use client";

import { m, type HTMLMotionProps } from "framer-motion";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import {
  reducedMotionVariants,
  revealVariants,
} from "@/lib/animations/variants";

export function Reveal({
  children,
  className,
  delay = 0,
  ...props
}: HTMLMotionProps<"div"> & { delay?: number }) {
  const reduced = useReducedMotion();
  const variants = reduced ? reducedMotionVariants : revealVariants;

  return (
    <m.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-60px" }}
      variants={variants}
      transition={{ delay }}
      className={className}
      {...props}
    >
      {children}
    </m.div>
  );
}
