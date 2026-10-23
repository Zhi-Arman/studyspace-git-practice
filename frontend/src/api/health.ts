export interface HealthResponse {
  status: 'ok';
  service: 'StudySpace';
  version: '0.4.0';
}

export type HealthErrorCode = 'network' | 'http' | 'invalid_response' | 'timeout';

export class HealthError extends Error {
  constructor(public readonly code: HealthErrorCode, message: string) {
    super(message);
    this.name = 'HealthError';
  }
}

function isHealthResponse(value: unknown): value is HealthResponse {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false;
  const result = value as Record<string, unknown>;
  return result.status === 'ok' && result.service === 'StudySpace' && result.version === '0.4.0';
}

/** A successful HTTP status alone does not prove that the API contract matches. */
export async function getHealth(
  { signal, timeoutMs = 5000 }: { signal?: AbortSignal; timeoutMs?: number } = {},
): Promise<HealthResponse> {
  const controller = new AbortController();
  let timedOut = false;
  const cancel = () => controller.abort();
  if (signal?.aborted) throw new DOMException('Request cancelled', 'AbortError');
  signal?.addEventListener('abort', cancel, { once: true });
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  try {
    const response = await fetch('/api/v1/health', {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    });
    if (!response.ok) throw new HealthError('http', `HTTP ${response.status}`);
    let result: unknown;
    try {
      result = await response.json();
    } catch {
      throw new HealthError('invalid_response', 'Expected a JSON health response');
    }
    if (!isHealthResponse(result)) {
      throw new HealthError('invalid_response', 'Health response does not match version 0.4.0');
    }
    return result;
  } catch (error) {
    if (timedOut) throw new HealthError('timeout', 'Health request exceeded the time limit');
    if (signal?.aborted) throw error;
    if (error instanceof HealthError) throw error;
    throw new HealthError('network', 'The API could not be reached');
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', cancel);
  }
}
