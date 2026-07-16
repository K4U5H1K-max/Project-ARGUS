"use client";

import { Menu, X } from "lucide-react";
import { useState } from "react";

import { Logo } from "@/components/common/Logo";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { Button, buttonClassName } from "@/components/ui/Button";
import { useActiveSection } from "@/hooks/useActiveSection";
import { useScrollPosition } from "@/hooks/useScrollPosition";
import { NAV_ITEMS, SITE } from "@/lib/theme/tokens";
import { cn } from "@/lib/utils/cn";

const SECTION_IDS = [
  "home",
  "pipeline",
  "digital-twin",
  "risk",
  "intelligence",
  "contact",
];

export function TopNav() {
  const scrolled = useScrollPosition(48);
  const activeId = useActiveSection(SECTION_IDS);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-0 z-50 transition-all duration-300",
        scrolled
          ? "border-b border-border-subtle bg-bg-base/80 shadow-elevation-1 backdrop-blur-xl"
          : "bg-transparent",
      )}
    >
      <nav
        className="mx-auto flex h-16 max-w-wide items-center justify-between px-6 md:px-8"
        aria-label="Main navigation"
      >
        <a href="#home" className="shrink-0" aria-label="ARGUS home">
          <Logo />
        </a>

        {/* Desktop links */}
        <ul className="hidden items-center gap-1 lg:flex">
          {NAV_ITEMS.map((item) => {
            const id = item.href.replace("#", "");
            const isActive = activeId === id;
            return (
              <li key={item.href}>
                <a
                  href={item.href}
                  className={cn(
                    "rounded-full px-3 py-1.5 text-sm transition-colors duration-300",
                    isActive
                      ? "bg-accent-cyan/10 text-accent-cyan"
                      : "text-text-secondary hover:text-text-primary",
                  )}
                  aria-current={isActive ? "page" : undefined}
                >
                  {item.label}
                </a>
              </li>
            );
          })}
        </ul>

        <div className="hidden items-center gap-3 md:flex">
          <ThemeToggle />
          <a
            href={SITE.dashboard}
            className={buttonClassName({ variant: "primary", size: "sm" })}
          >
            View Dashboard
          </a>
          <a
            href={SITE.github}
            target="_blank"
            rel="noopener noreferrer"
            className={buttonClassName({ variant: "ghost", size: "sm" })}
          >
            GitHub
          </a>
        </div>

        {/* Mobile menu toggle */}
        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle />
          <Button
            variant="ghost"
            size="sm"
            className="h-10 w-10 rounded-full p-0"
            onClick={() => setMobileOpen((o) => !o)}
            aria-expanded={mobileOpen}
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
          >
            {mobileOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>
        </div>
      </nav>

      {/* Mobile drawer */}
      {mobileOpen ? (
        <div className="border-t border-border-subtle bg-bg-base/95 backdrop-blur-xl md:hidden">
          <ul className="flex flex-col gap-1 px-6 py-4">
            {NAV_ITEMS.map((item) => {
              const id = item.href.replace("#", "");
              const isActive = activeId === id;
              return (
                <li key={item.href}>
                  <a
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "block rounded-lg px-3 py-2.5 text-sm",
                      isActive
                        ? "bg-accent-cyan/10 text-accent-cyan"
                        : "text-text-secondary",
                    )}
                  >
                    {item.label}
                  </a>
                </li>
              );
            })}
            <li className="mt-2 flex flex-col gap-2 border-t border-border-subtle pt-4">
              <a
                href={SITE.dashboard}
                className={buttonClassName({
                  variant: "primary",
                  size: "md",
                  className: "w-full",
                })}
              >
                View Dashboard
              </a>
              <a
                href={SITE.github}
                target="_blank"
                rel="noopener noreferrer"
                className={buttonClassName({
                  variant: "ghost",
                  size: "md",
                  className: "w-full",
                })}
              >
                GitHub
              </a>
            </li>
          </ul>
        </div>
      ) : null}
    </header>
  );
}
