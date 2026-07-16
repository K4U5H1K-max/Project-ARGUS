import { BookOpen, Code2, LayoutDashboard, Mail } from "lucide-react";

import { Logo } from "@/components/common/Logo";
import { Divider } from "@/components/ui/Divider";
import { Container } from "@/components/ui/Container";
import { SITE } from "@/lib/theme/tokens";

const footerLinks = {
  product: [
    { label: "Pipeline", href: "#pipeline" },
    { label: "Digital Twin", href: "#digital-twin" },
    { label: "Risk Engine", href: "#risk" },
    { label: "Intelligence", href: "#intelligence" },
  ],
  resources: [
    { label: "Documentation", href: SITE.docs, external: true },
    { label: "GitHub", href: SITE.github, external: true },
    { label: "Dashboard", href: SITE.dashboard },
    { label: "Contact", href: "#contact" },
  ],
};

export function Footer() {
  return (
    <footer
      id="contact"
      className="relative border-t border-border-subtle bg-bg-elevated/50"
    >
      <Container className="py-16 md:py-20">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-4 lg:col-span-2">
            <Logo />
            <p className="max-w-sm text-sm leading-relaxed text-text-secondary">
              {SITE.description}
            </p>
            <p className="font-mono text-xs text-text-muted">
              Deterministic · Explainable · Replayable
            </p>
          </div>

          <div>
            <h3 className="mb-4 font-mono text-xs uppercase tracking-[0.15em] text-text-muted">
              Platform
            </h3>
            <ul className="space-y-2">
              {footerLinks.product.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-sm text-text-secondary transition-colors hover:text-accent-cyan"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="mb-4 font-mono text-xs uppercase tracking-[0.15em] text-text-muted">
              Resources
            </h3>
            <ul className="space-y-2">
              {footerLinks.resources.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    target={link.external ? "_blank" : undefined}
                    rel={link.external ? "noopener noreferrer" : undefined}
                    className="inline-flex items-center gap-2 text-sm text-text-secondary transition-colors hover:text-accent-cyan"
                  >
                    {link.label === "GitHub" && (
                      <Code2 className="h-3.5 w-3.5" aria-hidden />
                    )}
                    {link.label === "Documentation" && (
                      <BookOpen className="h-3.5 w-3.5" aria-hidden />
                    )}
                    {link.label === "Dashboard" && (
                      <LayoutDashboard className="h-3.5 w-3.5" aria-hidden />
                    )}
                    {link.label === "Contact" && (
                      <Mail className="h-3.5 w-3.5" aria-hidden />
                    )}
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <Divider className="my-10" variant="blueprint" />

        <div className="flex flex-col items-center justify-between gap-4 text-center sm:flex-row sm:text-left">
          <p className="text-xs text-text-muted">
            © {new Date().getFullYear()} ARGUS. Industrial Safety Intelligence
            Platform.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
            <a
              href="#contact"
              className="transition-colors hover:text-accent-cyan"
            >
              Privacy
            </a>
            <a
              href="#contact"
              className="transition-colors hover:text-accent-cyan"
            >
              Terms
            </a>
            <span>Event-driven · Knowledge Graph · Geo Intelligence</span>
          </div>
        </div>
      </Container>
    </footer>
  );
}
