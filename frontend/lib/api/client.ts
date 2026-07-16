import { ApiError, type FetchResult } from "@/lib/api/types";

const DEFAULT_TIMEOUT_MS = 8_000;
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 600;

function getBaseUrl(): string {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/backend";
  }
  return (
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    process.env.API_BASE_URL ??
    "http://localhost:8000"
  );
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("Request timed out", "TIMEOUT");
    }
    throw new ApiError(
      error instanceof Error ? error.message : "Network request failed",
      "NETWORK",
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export interface ApiFetchOptions {
  timeoutMs?: number;
  retries?: number;
  headers?: Record<string, string>;
}

/**
 * Typed fetch wrapper with timeout, limited retry, and structured errors.
 * Uses same-origin proxy in browser to avoid CORS during demos.
 */
export async function apiFetch<T>(
  path: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, retries = MAX_RETRIES, headers } =
    options;

  const url = `${getBaseUrl().replace(/\/$/, "")}${path.startsWith("/") ? path : `/${path}`}`;

  let lastError: ApiError | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetchWithTimeout(
        url,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            "X-Client-Id": "argus-landing",
            ...headers,
          },
          cache: "no-store",
        },
        timeoutMs,
      );

      if (!response.ok) {
        throw new ApiError(
          `HTTP ${response.status}: ${response.statusText}`,
          "HTTP",
          response.status,
        );
      }

      try {
        return (await response.json()) as T;
      } catch {
        throw new ApiError("Failed to parse response JSON", "PARSE");
      }
    } catch (error) {
      lastError =
        error instanceof ApiError
          ? error
          : new ApiError("Unknown error", "UNKNOWN");

      if (attempt < retries && lastError.code !== "PARSE") {
        await sleep(RETRY_DELAY_MS * (attempt + 1));
        continue;
      }
      throw lastError;
    }
  }

  throw lastError ?? new ApiError("Unknown error", "UNKNOWN");
}

/** Safe fetch that never throws — returns null data on failure. */
export async function apiFetchSafe<T>(
  path: string,
  options?: ApiFetchOptions,
): Promise<FetchResult<T>> {
  try {
    const data = await apiFetch<T>(path, options);
    return { data, error: null };
  } catch (error) {
    return {
      data: null,
      error:
        error instanceof ApiError
          ? error
          : new ApiError("Unknown error", "UNKNOWN"),
    };
  }
}
