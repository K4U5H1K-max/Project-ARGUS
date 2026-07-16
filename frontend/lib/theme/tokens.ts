/**
 * ARGUS design tokens — single source of truth for programmatic access.
 * Visual values are defined as CSS variables in `app/globals.css`.
 */

export const NAV_ITEMS = [
  { label: "Home", href: "#home" },
  { label: "Pipeline", href: "#pipeline" },
  { label: "Digital Twin", href: "#digital-twin" },
  { label: "Risk", href: "#risk" },
  { label: "Intelligence", href: "#intelligence" },
  { label: "Contact", href: "#contact" },
] as const;

export const SITE = {
  name: "ARGUS",
  tagline: "Industrial Safety Intelligence Platform",
  description:
    "ARGUS transforms live operational telemetry into a Digital Twin, explainable risk assessments, and coordinated response—grounded in knowledge graphs, geospatial intelligence, and citation-backed guidance.",
  url: "https://argus.dev",
  github: "https://github.com/K4U5H1K-max/Project-ARGUS",
  docs: "http://localhost:8000/docs",
  dashboard: "/dashboard",
} as const;

export const MOTION = {
  fast: 0.14,
  base: 0.28,
  slow: 0.65,
  easing: [0.2, 0, 0, 1] as const,
} as const;
