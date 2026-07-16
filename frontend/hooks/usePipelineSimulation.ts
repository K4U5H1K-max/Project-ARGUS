"use client";

import { useSyncExternalStore } from "react";

/**
 * Shared client state for the interactive pipeline simulator.
 * Event Storm → Twin → Context → Risk stages respond to user trigger.
 */
export type PipelineStage =
  | "idle"
  | "event"
  | "twin"
  | "context"
  | "risk"
  | "done";

export const PIPELINE_STAGES: Exclude<PipelineStage, "idle" | "done">[] = [
  "event",
  "twin",
  "context",
  "risk",
];

const STAGE_SEQUENCE: PipelineStage[] = [
  "event",
  "twin",
  "context",
  "risk",
  "done",
];

type Snapshot = {
  stage: PipelineStage;
  eventLabel: string;
  running: boolean;
};

let snapshot: Snapshot = {
  stage: "idle",
  eventLabel: "",
  running: false,
};

const listeners = new Set<() => void>();

function emit() {
  listeners.forEach((l) => l());
}

function getSnapshot() {
  return snapshot;
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export async function runPipelineSimulation(
  label = "GAS_SENSOR · Battery_A",
) {
  if (snapshot.running) return;

  snapshot = { stage: "idle", eventLabel: label, running: true };
  emit();

  for (const next of STAGE_SEQUENCE) {
    snapshot = { ...snapshot, stage: next };
    emit();
    await new Promise((r) => setTimeout(r, 750));
  }

  snapshot = { ...snapshot, running: false };
  emit();

  await new Promise((r) => setTimeout(r, 1600));
  snapshot = { stage: "idle", eventLabel: "", running: false };
  emit();
}

export function usePipelineSimulation() {
  const snap = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);

  return {
    ...snap,
    stages: PIPELINE_STAGES,
    simulate: runPipelineSimulation,
  };
}
