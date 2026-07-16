"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api/endpoints";
import { mapHealthToStatus } from "@/lib/api/mappers";
import { queryKeys } from "@/lib/api/query-keys";
import { HEALTH_STATUS } from "@/lib/content/story";

const POLL_MS = 30_000;

export function useHealth() {
  const query = useQuery({
    queryKey: queryKeys.health,
    queryFn: api.health,
    refetchInterval: POLL_MS,
    refetchIntervalInBackground: false,
    retry: 1,
  });

  return {
    data: query.data ? mapHealthToStatus(query.data) : HEALTH_STATUS,
    isLive: query.isSuccess,
    isLoading: false,
    isFetching: query.isFetching,
    isError: query.isError,
  };
}
