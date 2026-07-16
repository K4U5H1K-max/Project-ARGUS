import { apiFetch } from "@/lib/api/client";
import type { GeoLayoutResponse, HealthResponse, RiskApiResponse } from "@/lib/api/types";

export const api = {
  health: () => apiFetch<HealthResponse>("/health"),
  readiness: () => apiFetch<HealthResponse>("/readiness"),
  riskCurrent: (params?: { plant_id?: string; zone_id?: string }) => {
    const search = new URLSearchParams();
    if (params?.plant_id) search.set("plant_id", params.plant_id);
    if (params?.zone_id) search.set("zone_id", params.zone_id);
    const qs = search.toString();
    return apiFetch<RiskApiResponse | null>(
      `/risk/current${qs ? `?${qs}` : ""}`,
    );
  },
  geoLayout: (params?: { plant_id?: string; zone_id?: string }) => {
    const search = new URLSearchParams();
    if (params?.plant_id) search.set("plant_id", params.plant_id);
    if (params?.zone_id) search.set("zone_id", params.zone_id);
    const qs = search.toString();
    return apiFetch<GeoLayoutResponse>(`/geo/layout${qs ? `?${qs}` : ""}`);
  },
} as const;
