import { useEffect, useState } from "react";
import { api, ApiError } from "./api/client";

/** Keys and abort cleanup keep old requests from overwriting a newer selection. */
export function useQuery<T>(path: string | null, revision = 0) {
  const key = `${path}|${revision}`;
  const [state, setState] = useState<{
    key: string;
    data?: T;
    error?: ApiError;
  }>({ key: "" });
  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    let active = true;
    api<T>(path, { signal: controller.signal }).then(
      (data) => {
        if (active) setState({ key, data });
      },
      (error) => {
        if (active && !controller.signal.aborted) setState({ key, error });
      },
    );
    return () => {
      active = false;
      controller.abort();
    };
  }, [path, key]);
  return {
    previousData: state.data,
    data: path && state.key === key ? state.data : undefined,
    error: path && state.key === key ? state.error : undefined,
    loading: Boolean(path && state.key !== key),
  };
}
