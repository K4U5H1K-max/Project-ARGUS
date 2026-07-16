"use client";

import { Moon, Sun } from "lucide-react";

import { useTheme } from "@/lib/theme/ThemeProvider";
import { cn } from "@/lib/utils/cn";

export interface ThemeToggleProps {
  className?: string;
}

export function ThemeToggle({ className }: ThemeToggleProps) {
  const { resolvedTheme, toggleTheme } = useTheme();
  const nextLabel = resolvedTheme === "dark" ? "light" : "dark";

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={cn(
        "inline-flex h-10 w-10 items-center justify-center rounded-full",
        "border border-border-subtle bg-bg-surface/60 text-text-secondary",
        "transition-all duration-300 hover:border-accent-cyan/30 hover:text-accent-cyan",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-cyan/50",
        className,
      )}
      aria-label={`Switch to ${nextLabel} mode`}
    >
      {resolvedTheme === "dark" ? (
        <Sun className="h-4 w-4" aria-hidden />
      ) : (
        <Moon className="h-4 w-4" aria-hidden />
      )}
    </button>
  );
}
