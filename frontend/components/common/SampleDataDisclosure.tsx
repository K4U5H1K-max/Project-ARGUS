import { Container } from "@/components/ui/Container";

/**
 * Single site-wide disclosure for illustrative landing data.
 * Prefer this over per-card "Sample data" badges for consistency.
 */
export function SampleDataDisclosure() {
  return (
    <div className="border-y border-border-subtle/80 bg-bg-elevated/40">
      <Container className="py-3">
        <p className="text-center font-mono text-[11px] leading-relaxed tracking-wide text-text-muted md:text-left">
          <span className="mr-2 inline-flex items-center rounded-full border border-signal-warning/30 bg-signal-warning/10 px-2 py-0.5 uppercase tracking-wider text-signal-warning">
            Sample data
          </span>
          Visualizations on this page use illustrative facility scenarios shaped
          like live ARGUS APIs. When the backend is connected, Reliability, Risk,
          and Geo sections upgrade to live telemetry automatically.
        </p>
      </Container>
    </div>
  );
}
