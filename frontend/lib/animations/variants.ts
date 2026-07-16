import type { Variants, Transition } from "framer-motion";

import { MOTION } from "@/lib/theme/tokens";

export const easeIndustrial: Transition["ease"] = MOTION.easing;

export const transitionFast: Transition = {
  duration: MOTION.fast,
  ease: easeIndustrial,
};

export const transitionBase: Transition = {
  duration: MOTION.base,
  ease: easeIndustrial,
};

export const transitionSlow: Transition = {
  duration: MOTION.slow,
  ease: easeIndustrial,
};

export const fadeVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};

export const slideUpVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
};

export const slideDownVariants: Variants = {
  hidden: { opacity: 0, y: -24 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 12 },
};

export const slideLeftVariants: Variants = {
  hidden: { opacity: 0, x: 24 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -12 },
};

export const slideRightVariants: Variants = {
  hidden: { opacity: 0, x: -24 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 12 },
};

export const scaleVariants: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.98 },
};

export const revealVariants: Variants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { ...transitionSlow, duration: 0.65 },
  },
};

export const staggerContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.03,
    },
  },
};

export const staggerItemVariants: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitionBase,
  },
};

export const pageTransitionVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: transitionBase },
  exit: { opacity: 0, transition: transitionFast },
};

/** Reduced-motion friendly: instant visibility, no transform. */
export const reducedMotionVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.01 } },
  exit: { opacity: 0, transition: { duration: 0.01 } },
};
