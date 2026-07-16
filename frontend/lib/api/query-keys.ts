export const queryKeys = {
  health: ["health"] as const,
  readiness: ["readiness"] as const,
  riskCurrent: (plantId?: string, zoneId?: string) =>
    ["risk", "current", plantId ?? "all", zoneId ?? "all"] as const,
  geoLayout: (plantId?: string, zoneId?: string) =>
    ["geo", "layout", plantId ?? "all", zoneId ?? "all"] as const,
};
