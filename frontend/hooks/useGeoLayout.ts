"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/query-keys";
import type { GeoLayoutResponse } from "@/lib/api/types";

export function useGeoLayout(plantId?: string, zoneId?: string) {
  const query = useQuery({
    queryKey: queryKeys.geoLayout(plantId, zoneId),
    queryFn: () => api.geoLayout({ plant_id: plantId, zone_id: zoneId }),
    staleTime: 60_000,
    retry: 1,
  });

  return {
    layout: query.data as GeoLayoutResponse | undefined,
    isLive: Boolean(query.data?.features?.length),
    isLoading: false,
    isFetching: query.isFetching,
    isError: query.isError,
  };
}
