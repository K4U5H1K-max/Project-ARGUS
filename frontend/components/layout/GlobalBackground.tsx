"use client";

import { cn } from "@/lib/utils/cn";

/**
 * Premium ambient background — blueprint grid, gradient glow,
 * telemetry particles, scan line, and noise texture. Lightweight CSS + SVG.
 */
export function GlobalBackground() {
  return (
    <div
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
      aria-hidden
    >
      {/* Base gradient wash */}
      <div className="absolute inset-0 bg-bg-base" />

      {/* Ambient gradient orbs */}
      <div
        className={cn(
          "absolute -left-1/4 top-0 h-[60vh] w-[60vw] rounded-full",
          "bg-accent-cyan/10 blur-[120px] animate-gradient-shift",
        )}
      />
      <div
        className={cn(
          "absolute -right-1/4 bottom-0 h-[50vh] w-[50vw] rounded-full",
          "bg-accent-violet/8 blur-[100px] animate-gradient-shift",
          "[animation-delay:4s]",
        )}
      />
      <div
        className={cn(
          "absolute left-1/3 top-1/2 h-[35vh] w-[35vw] -translate-y-1/2 rounded-full",
          "bg-accent-cyan/[0.04] blur-[80px] animate-gradient-shift",
          "[animation-delay:8s]",
        )}
      />

      {/* Blueprint grid */}
      <svg
        className="absolute inset-0 h-full w-full opacity-[var(--grid-opacity)] animate-grid-drift"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern
            id="blueprint-grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="currentColor"
              strokeWidth="0.5"
              className="text-accent-cyan"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#blueprint-grid)" />
      </svg>

      {/* Sparse grid highlight cells */}
      <div className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]">
        {Array.from({ length: 6 }).map((_, i) => (
          <span
            key={i}
            className="absolute h-10 w-10 border border-accent-cyan/40 animate-grid-highlight"
            style={{
              left: `${12 + (i * 14) % 70}%`,
              top: `${18 + (i * 17) % 60}%`,
              animationDelay: `${i * 1.4}s`,
            }}
          />
        ))}
      </div>

      {/* Ambient topology lines */}
      <svg
        className="absolute inset-0 h-full w-full opacity-[0.04] dark:opacity-[0.07]"
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMid slice"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M0 450 Q360 350 720 450 T1440 450"
          fill="none"
          stroke="currentColor"
          strokeWidth="1"
          className="text-accent-cyan"
          strokeDasharray="8 12"
          style={{ animation: "line-flow 30s linear infinite" }}
        />
        <path
          d="M0 600 Q480 500 960 600 T1920 600"
          fill="none"
          stroke="currentColor"
          strokeWidth="0.5"
          className="text-accent-violet"
          strokeDasharray="4 8"
          style={{ animation: "line-flow 40s linear infinite reverse" }}
        />
        <path
          d="M0 280 Q400 220 800 300 T1440 260"
          fill="none"
          stroke="currentColor"
          strokeWidth="0.5"
          className="text-accent-cyan"
          strokeDasharray="2 10"
          style={{ animation: "line-flow 50s linear infinite" }}
        />
      </svg>

      {/* Blueprint scan line */}
      <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-accent-cyan/[0.04] via-transparent to-transparent animate-scan-line" />

      {/* Floating telemetry particles */}
      {Array.from({ length: 16 }).map((_, i) => (
        <span
          key={i}
          className={cn(
            "absolute rounded-full animate-telemetry-float",
            i % 3 === 0
              ? "h-1.5 w-1.5 bg-accent-violet/35"
              : "h-1 w-1 bg-accent-cyan/40",
          )}
          style={{
            left: `${6 + (i * 5.8) % 88}%`,
            top: `${10 + (i * 9.5) % 78}%`,
            animationDelay: `${i * 0.55}s`,
            animationDuration: `${6.5 + (i % 5)}s`,
          }}
        />
      ))}

      {/* Tiny pulse nodes */}
      {Array.from({ length: 4 }).map((_, i) => (
        <span
          key={`pulse-${i}`}
          className="absolute h-1 w-1 rounded-full bg-accent-cyan/50"
          style={{
            left: `${20 + i * 22}%`,
            top: `${25 + i * 15}%`,
          }}
        >
          <span className="absolute inset-0 rounded-full bg-accent-cyan/40 animate-node-pulse" />
        </span>
      ))}

      {/* Noise texture overlay */}
      <div
        className="absolute inset-0 opacity-[var(--noise-opacity)]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundRepeat: "repeat",
          backgroundSize: "128px 128px",
        }}
      />

      {/* Vignette */}
      <div className="absolute inset-0 bg-gradient-to-b from-bg-base/30 via-transparent to-bg-base/85" />
    </div>
  );
}
