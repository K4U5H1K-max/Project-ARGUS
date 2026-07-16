"use client";

import { m, type HTMLMotionProps } from "framer-motion";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import {
  reducedMotionVariants,
  staggerContainerVariants,
  staggerItemVariants,
} from "@/lib/animations/variants";

export function Stagger({
  children,
  className,
  ...props
}: HTMLMotionProps<"div">) {
  const reduced = useReducedMotion();
  const containerVariants = reduced
    ? reducedMotionVariants
    : staggerContainerVariants;

  return (
    <m.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-60px" }}
      variants={containerVariants}
      className={className}
      {...props}
    >
      {children}
    </m.div>
  );
}

export function StaggerItem({
  children,
  className,
  ...props
}: HTMLMotionProps<"div">) {
  const reduced = useReducedMotion();
  const itemVariants = reduced ? reducedMotionVariants : staggerItemVariants;

  return (
    <m.div variants={itemVariants} className={className} {...props}>
      {children}
    </m.div>
  );
}
