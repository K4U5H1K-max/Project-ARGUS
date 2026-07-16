"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api/endpoints";
import { mapHealthToStatus } from "@/lib/api/mappers";
import { queryKeys } from "@/lib/api/query-keys";
import { HEALTH_STATUS } from "@/lib/content/story";

const POLL_MS = 30_000;

export function useReadiness() {
  const query = useQuery({
    queryKey: queryKeys.readiness,
    queryFn: api.readiness,
    refetchInterval: POLL_MS,
    refetchIntervalInBackground: false,
    retry: 1,
  });

  const health = query.data ? mapHealthToStatus(query.data) : HEALTH_STATUS;
  const isReady =
    health.database &&
    health.kafka &&
    health.outbox_worker &&
    health.replay_service &&
    health.neo4j;

  return {
    health,
    isReady,
    isLive: query.isSuccess,
    isLoading: false,
    isFetching: query.isFetching,
    isError: query.isError,
  };
}
