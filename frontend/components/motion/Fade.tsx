"use client";

import { m, type HTMLMotionProps } from "framer-motion";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import {
  fadeVariants,
  reducedMotionVariants,
  transitionBase,
} from "@/lib/animations/variants";

export function Fade({
  children,
  className,
  ...props
}: HTMLMotionProps<"div">) {
  const reduced = useReducedMotion();
  const variants = reduced ? reducedMotionVariants : fadeVariants;

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
