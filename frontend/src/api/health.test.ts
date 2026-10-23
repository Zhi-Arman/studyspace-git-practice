import { describe, expect, it, vi } from 'vitest';
import { getHealth, HealthError } from './health';

const valid = { status: 'ok', service: 'StudySpace', version: '0.4.0' };

describe('health API contract', () => {
  it('accepts a matching JSON contract and uses the same-origin API path', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...valid, extra: true })));
    vi.stubGlobal('fetch', fetchMock);
    await expect(getHealth()).resolves.toMatchObject(valid);
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/health', expect.objectContaining({ cache: 'no-store' }));
  });

  it.each([null, [], {}, { ...valid, status: 'failed' }, { ...valid, service: 'Other' }, { ...valid, version: '0.2.0' }])('rejects an incompatible response: %j', async (body) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(body))));
    await expect(getHealth()).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it('rejects an HTTP failure even if its body resembles a successful response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(valid), { status: 503 })));
    await expect(getHealth()).rejects.toMatchObject({ code: 'http' });
  });

  it('rejects non-JSON responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>Unavailable</html>')));
    await expect(getHealth()).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it('reports a network failure', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
    await expect(getHealth()).rejects.toMatchObject({ code: 'network' });
  });

  it('aborts a request that exceeds the timeout', async () => {
    vi.stubGlobal('fetch', vi.fn((_url, init: RequestInit) => new Promise((_resolve, reject) => {
      init.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    })));
    await expect(getHealth({ timeoutMs: 10 })).rejects.toEqual(expect.objectContaining<Partial<HealthError>>({ code: 'timeout' }));
  });

  it('does not send an already cancelled request', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const controller = new AbortController();
    controller.abort();
    await expect(getHealth({ signal: controller.signal })).rejects.toMatchObject({ name: 'AbortError' });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
