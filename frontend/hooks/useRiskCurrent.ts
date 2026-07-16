"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api/endpoints";
import { mapRiskApiToAssessment } from "@/lib/api/mappers";
import { queryKeys } from "@/lib/api/query-keys";
import { RISK_ASSESSMENT } from "@/lib/content/story";

const POLL_MS = 20_000;

/**
 * Landing-page risk hook: always returns displayable data immediately.
 * Never blocks the UI on network — sample data shows until live data arrives.
 */
export function useRiskCurrent(plantId?: string, zoneId?: string) {
  const query = useQuery({
    queryKey: queryKeys.riskCurrent(plantId, zoneId),
    queryFn: async () => {
      const result = await api.riskCurrent({
        plant_id: plantId,
        zone_id: zoneId,
      });
      return result;
    },
    refetchInterval: POLL_MS,
    refetchIntervalInBackground: false,
    retry: 1,
    // Never suspend the section on first fetch
    placeholderData: undefined,
  });

  const live =
    query.data && query.data !== null
      ? mapRiskApiToAssessment(query.data)
      : null;

  return {
    data: live ?? RISK_ASSESSMENT,
    isLive: live !== null,
    // Only true on the very first fetch with no fallback shown yet — we always
    // have fallback, so landing UI never waits on skeleton.
    isLoading: false,
    isFetching: query.isFetching,
    isError: query.isError,
  };
}
