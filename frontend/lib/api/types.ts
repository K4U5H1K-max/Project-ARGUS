/** API response types aligned with FastAPI backend contracts. */

export interface HealthResponse {
  status: "ok" | "degraded";
  database: boolean;
  kafka: boolean;
  outbox_worker: boolean;
  replay_service: boolean;
  neo4j: boolean;
  graph_bootstrap: boolean;
}

export interface RiskApiResponse {
  risk_id: string;
  plant_id: string;
  zone_id: string;
  score: number;
  level: string;
  confidence: number;
  status: string;
  timestamp: string;
  recommendations: string[] | null;
  explanation: string | null;
  trace: Record<string, unknown> | null;
}

export interface GeoFeature {
  type: "Feature";
  geometry: {
    type: string;
    coordinates: number[] | number[][] | number[][][];
  };
  properties: Record<string, unknown>;
}

export interface GeoLayoutResponse {
  type: "FeatureCollection";
  features: GeoFeature[];
  summary?: {
    plant_id: string;
    zone_id: string;
    layout_type: string;
    feature_count: number;
    risk_id: string;
  };
}

export type ApiErrorCode =
  | "NETWORK"
  | "TIMEOUT"
  | "HTTP"
  | "PARSE"
  | "UNKNOWN";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code: ApiErrorCode,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface FetchResult<T> {
  data: T | null;
  error: ApiError | null;
  fromCache?: boolean;
}
