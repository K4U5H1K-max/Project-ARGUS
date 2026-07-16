"use client";

import { m } from "framer-motion";
import { useState } from "react";

import { useReducedMotion } from "@/hooks/useReducedMotion";
import {
  GRAPH_NODES,
  GRAPH_EDGES,
  type GraphNode,
} from "@/lib/content/story";
import { Panel } from "@/components/ui/Panel";
import { BlueprintOverlay } from "@/components/viz/BlueprintOverlay";
import { cn } from "@/lib/utils/cn";

type ViewMode = "neighbors" | "impact" | "dependencies";

/** Interactive knowledge graph — nodes, edges, impact paths. */
export function GraphViz({ className }: { className?: string }) {
  const reduced = useReducedMotion();
  const [selected, setSelected] = useState<GraphNode>(
    () => GRAPH_NODES.find((n) => n.id === "hz-gas-cloud") ?? GRAPH_NODES[1],
  );
  const [viewMode, setViewMode] = useState<ViewMode>("impact");

  const connectedIds = new Set<string>();
  GRAPH_EDGES.forEach((edge) => {
    if (edge.source === selected.id || edge.target === selected.id) {
      connectedIds.add(edge.source);
      connectedIds.add(edge.target);
    }
  });
  connectedIds.add(selected.id);

  const highlightEdges = GRAPH_EDGES.filter(
    (e) =>
      viewMode === "neighbors"
        ? e.source === selected.id || e.target === selected.id
        : viewMode === "impact"
          ? e.type === "THREATENS" || e.type === "DEPENDS_ON"
          : e.type === "DEPENDS_ON" || e.type === "CONTAINS",
  );

  return (
    <div className={cn("relative w-full", className)}>
      <Panel glow="violet" className="relative overflow-hidden p-4 md:p-6">
        <BlueprintOverlay patternId="graph-grid" />

        <p className="relative mb-3 font-mono text-[10px] uppercase tracking-[0.15em] text-text-muted">
          GET /graph/* — Knowledge Graph
        </p>

        <div className="relative mb-3 flex flex-wrap gap-2">
          {(["neighbors", "impact", "dependencies"] as ViewMode[]).map(
            (mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => setViewMode(mode)}
                className={cn(
                  "rounded-chip border px-3 py-1 font-mono text-xs capitalize transition-all",
                  viewMode === mode
                    ? "border-accent-violet/40 bg-accent-violet/10 text-accent-violet"
                    : "border-border-subtle text-text-secondary",
                )}
                aria-pressed={viewMode === mode}
              >
                {mode}
              </button>
            ),
          )}
        </div>

        <svg
          viewBox="0 0 240 240"
          className="mx-auto h-52 w-full max-w-[300px]"
          aria-label="Knowledge graph topology"
          role="img"
        >
          {highlightEdges.map((edge, i) => {
            const source = GRAPH_NODES.find((n) => n.id === edge.source)!;
            const target = GRAPH_NODES.find((n) => n.id === edge.target)!;
            return (
              <m.line
                key={`${edge.source}-${edge.target}`}
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke="currentColor"
                strokeWidth="1.5"
                className="text-accent-violet/60"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{
                  delay: reduced ? 0 : i * 0.08,
                  duration: 0.5,
                }}
              />
            );
          })}

          {GRAPH_NODES.map((node) => {
            const isConnected = connectedIds.has(node.id);
            const isSelected = node.id === selected.id;
            return (
              <g
                key={node.id}
                className="cursor-pointer"
                onClick={() => setSelected(node)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") setSelected(node);
                }}
                role="button"
                tabIndex={0}
                aria-label={`${node.label} (${node.type})`}
                aria-pressed={isSelected}
              >
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={isSelected ? 12 : 8}
                  className={cn(
                    "transition-all duration-300",
                    isSelected
                      ? "fill-accent-violet/30 stroke-accent-violet"
                      : isConnected
                        ? "fill-bg-surface stroke-accent-violet/50"
                        : "fill-bg-surface/50 stroke-border-subtle opacity-40",
                  )}
                  strokeWidth="1.5"
                />
                <text
                  x={node.x}
                  y={node.y + 22}
                  textAnchor="middle"
                  className="fill-text-muted font-mono text-[6px]"
                >
                  {node.type}
                </text>
              </g>
            );
          })}
        </svg>

        <m.div
          key={`${selected.id}-${viewMode}`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-3 space-y-2"
        >
          <div className="rounded-chip border border-accent-violet/30 bg-accent-violet/5 p-3">
            <p className="font-mono text-[10px] uppercase tracking-wider text-accent-violet">
              Blast-radius focus
            </p>
            <p className="mt-1 font-mono text-sm text-text-primary">
              {selected.label}
            </p>
            <p className="font-mono text-[10px] text-text-muted">
              {viewMode} · {highlightEdges.length} relationships illuminated
            </p>
          </div>
          <p className="font-mono text-[10px] text-text-muted">
            Toggle impact / dependencies to see how a hazard cascades across
            workers, equipment, and zones.
          </p>
        </m.div>
      </Panel>
    </div>
  );
}
