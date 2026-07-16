"use client";

import { m, type HTMLMotionProps } from "framer-motion";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import {
  reducedMotionVariants,
  slideUpVariants,
  slideDownVariants,
  slideLeftVariants,
  slideRightVariants,
  transitionBase,
} from "@/lib/animations/variants";

type SlideDirection = "up" | "down" | "left" | "right";

const directionMap = {
  up: slideUpVariants,
  down: slideDownVariants,
  left: slideLeftVariants,
  right: slideRightVariants,
};

export interface SlideProps extends HTMLMotionProps<"div"> {
  direction?: SlideDirection;
}

export function Slide({
  direction = "up",
  children,
  className,
  ...props
}: SlideProps) {
  const reduced = useReducedMotion();
  const variants = reduced ? reducedMotionVariants : directionMap[direction];

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
