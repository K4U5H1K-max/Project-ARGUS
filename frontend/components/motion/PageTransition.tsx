"use client";

import { m, type HTMLMotionProps } from "framer-motion";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import {
  pageTransitionVariants,
  reducedMotionVariants,
} from "@/lib/animations/variants";

/** Wraps page-level content with enter/exit transitions. */
export function PageTransition({
  children,
  className,
  ...props
}: HTMLMotionProps<"div">) {
  const reduced = useReducedMotion();
  const variants = reduced ? reducedMotionVariants : pageTransitionVariants;

  return (
    <m.div
      initial="hidden"
      animate="visible"
      exit="exit"
      variants={variants}
      className={className}
      {...props}
    >
      {children}
    </m.div>
  );
}
