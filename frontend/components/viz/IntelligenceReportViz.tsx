"use client";

import { m } from "framer-motion";
import { useState } from "react";

import { INTELLIGENCE_REPORT } from "@/lib/content/story";
import { Badge } from "@/components/ui/Badge";
import { Chip } from "@/components/ui/Chip";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { cn } from "@/lib/utils/cn";

/** Citation-backed intelligence report with evidence assembly. */
export function IntelligenceReportViz({ className }: { className?: string }) {
  const [activeCitation, setActiveCitation] = useState<string | null>(null);
  const report = INTELLIGENCE_REPORT;

  return (
    <div className={cn("relative w-full", className)}>
      <Panel glow="violet" className="relative overflow-hidden p-4 md:p-6">
        <BlueprintOverlay patternId="intel-grid" />

        <p className="relative mb-4 font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
          GET /intelligence/report/{'{risk_id}'}
        </p>

        <m.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative space-y-4"
        >
          <p className="text-sm leading-relaxed text-text-primary">
            {report.summary}
          </p>

          <div className="space-y-2">
            <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
              Regulations
            </p>
            {report.regulations.map((reg, i) => (
              <m.p
                key={reg}
                initial={{ opacity: 0, x: -8 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-xs text-text-secondary"
              >
                § {reg}
              </m.p>
            ))}
          </div>

          <div className="space-y-2">
            <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
              Root Causes
            </p>
            {report.root_causes.map((cause) => (
              <Badge key={cause} level="warning">
                {cause}
              </Badge>
            ))}
          </div>

          <div className="space-y-2">
            <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
              Citations
            </p>
            <div className="flex flex-wrap gap-2">
              {report.citations.map((cite) => (
                <button
                  key={cite.id}
                  type="button"
                  onClick={() =>
                    setActiveCitation(
                      activeCitation === cite.id ? null : cite.id,
                    )
                  }
                  className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-violet/50"
                  aria-expanded={activeCitation === cite.id}
                >
                  <Chip active={activeCitation === cite.id}>
                    {cite.source}
                  </Chip>
                </button>
              ))}
            </div>
          </div>

          {activeCitation ? (
            <m.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="rounded-chip border border-accent-violet/30 bg-accent-violet/5 p-3"
            >
              <p className="font-mono text-[10px] text-accent-violet">
                {
                  report.citations.find((c) => c.id === activeCitation)
                    ?.source
                }
              </p>
              <p className="mt-1 text-xs italic text-text-secondary">
                &ldquo;
                {
                  report.citations.find((c) => c.id === activeCitation)
                    ?.excerpt
                }
                &rdquo;
              </p>
            </m.div>
          ) : null}
        </m.div>
      </Panel>
    </div>
  );
}
