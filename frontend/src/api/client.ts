export interface User {
  id: number;
  username: string;
  display_name: string;
  role: "STUDENT" | "ADMIN";
  enabled: boolean;
  identity_mode: "LOCAL_ONLY";
}
export interface Policy {
  today: string;
  server_now?: string;
  timezone: string;
  advance_days: number;
  granularity_minutes: number;
  max_duration_hours: number;
  identity_mode: string;
}
export interface Room {
  id: number;
  name: string;
  campus: string;
  building: string;
  floor: number;
  kind: "CLASSROOM" | "STUDY_ROOM";
  description: string;
  enabled: boolean;
  capacity: number;
  seat_count: number;
  opens_at: string | null;
  closes_at: string | null;
  regular_opens_at: string;
  regular_closes_at: string;
  closed: boolean;
}
export interface Seat {
  id: number;
  room_id: number;
  code: string;
  enabled: boolean;
  available?: boolean;
}
export interface Booking {
  id: number;
  seat_id: number;
  seat_code: string;
  room_id: number;
  room_name: string;
  business_date: string;
  starts_at: string;
  ends_at: string;
  created_at: string;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  status: "UPCOMING" | "ONGOING" | "COMPLETED" | "CANCELLED";
  can_cancel: boolean;
  username?: string | null;
  display_name?: string | null;
}
export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
export interface SeatResult {
  room: Room;
  items: Seat[];
}
export class ApiError extends Error {
  constructor(
    public code: string,
    public status = 0,
  ) {
    super(code);
    this.name = "ApiError";
  }
}

export async function api<T>(
  path: string,
  options: {
    method?: string;
    body?: unknown;
    signal?: AbortSignal;
    quietUnauthorized?: boolean;
  } = {},
): Promise<T> {
  const controller = new AbortController();
  const cancel = () => controller.abort();
  if (options.signal?.aborted) throw new DOMException("Aborted", "AbortError");
  options.signal?.addEventListener("abort", cancel, { once: true });
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, 15000);
  try {
    const response = await fetch(`/api/v1${path}`, {
      method: options.method || "GET",
      credentials: "same-origin",
      cache: "no-store",
      headers: {
        Accept: "application/json",
        ...(options.method
          ? { "X-StudySpace-Request": "1", "Content-Type": "application/json" }
          : {}),
      },
      body:
        options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: controller.signal,
    });
    if (response.status === 204) return undefined as T;
    let value;
    try {
      value = await response.json();
    } catch {
      throw new ApiError("INVALID_RESPONSE", response.status);
    }
    if (!response.ok) {
      const code =
        typeof value?.error?.code === "string"
          ? value.error.code
          : "REQUEST_FAILED";
      if (
        response.status === 401 &&
        code === "AUTH_REQUIRED" &&
        !options.quietUnauthorized
      )
        window.dispatchEvent(new Event("studyspace:session-ended"));
      throw new ApiError(code, response.status);
    }
    return value as T;
  } catch (error) {
    if (options.signal?.aborted) throw error;
    if (error instanceof ApiError) throw error;
    throw new ApiError(timedOut ? "TIMEOUT" : "NETWORK");
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener("abort", cancel);
  }
}

export function query(
  values: Record<string, string | number | null | undefined>,
) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(values))
    if (value !== undefined && value !== null && value !== "")
      params.set(key, String(value));
  return params.toString();
}
