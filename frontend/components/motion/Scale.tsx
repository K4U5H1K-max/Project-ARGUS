"use client";

import { m, type HTMLMotionProps } from "framer-motion";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import {
  reducedMotionVariants,
  scaleVariants,
  transitionBase,
} from "@/lib/animations/variants";

export function Scale({
  children,
  className,
  ...props
}: HTMLMotionProps<"div">) {
  const reduced = useReducedMotion();
  const variants = reduced ? reducedMotionVariants : scaleVariants;

  return (
    <m.div
      initial="hidden"
      animate="visible"
      exit="exit"
      variants={variants}
      transition={transitionBase}
      className={className}
      {...props}
    >
      {children}
    </m.div>
  );
}
