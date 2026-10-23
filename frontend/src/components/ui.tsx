import { useEffect, useId, useRef } from "react";
import type { ReactNode } from "react";
import { errorText } from "../i18n";
import type { T } from "../i18n";

export function ErrorBanner({
  error,
  t,
  retry,
}: {
  error: unknown;
  t: T;
  retry?: () => void;
}) {
  if (!error) return null;
  return (
    <div className="error-banner" role="alert">
      <span>{errorText(error, t)}</span>
      {retry && (
        <button className="text-button" onClick={retry}>
          {t("retry")}
        </button>
      )}
    </div>
  );
}
export function Loading({ t }: { t: T }) {
  return (
    <div className="loading" role="status">
      <span className="spinner" />
      {t("loading")}
    </div>
  );
}
export function Empty({ children }: { children: ReactNode }) {
  return (
    <div className="empty-state">
      <span aria-hidden="true">⌑</span>
      <p>{children}</p>
    </div>
  );
}
export function Modal({
  title,
  children,
  close,
  t,
}: {
  title: string;
  children: ReactNode;
  close: () => void;
  t: T;
}) {
  const id = useId();
  const container = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    container.current
      ?.querySelector<HTMLElement>("input, button, select")
      ?.focus();
    return () => {
      document.body.style.overflow = overflow;
      previous?.focus();
    };
  }, []);
  return (
    <div className="modal-backdrop">
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={id}
        ref={container}
        onKeyDown={(event) => {
          if (event.key === "Escape") {
            event.preventDefault();
            close();
          }
          if (event.key === "Tab") {
            const controls = container.current?.querySelectorAll<HTMLElement>(
              'button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex="0"]',
            );
            if (!controls?.length) return;
            const first = controls[0],
              last = controls[controls.length - 1];
            if (event.shiftKey && document.activeElement === first) {
              event.preventDefault();
              last.focus();
            }
            if (!event.shiftKey && document.activeElement === last) {
              event.preventDefault();
              first.focus();
            }
          }
        }}
      >
        <div className="modal-heading">
          <h2 id={id}>{title}</h2>
          <button
            className="icon-button"
            onClick={close}
            aria-label={t("close")}
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
export function Pagination({
  page,
  total,
  size = 20,
  change,
  t,
}: {
  page: number;
  total: number;
  size?: number;
  change: (page: number) => void;
  t: T;
}) {
  if (total <= size && page === 1) return null;
  return (
    <div className="pagination">
      <button
        className="secondary-button"
        disabled={page <= 1}
        onClick={() => change(page - 1)}
      >
        {t("previous")}
      </button>
      <span>
        {t("page")} {page} / {Math.max(1, Math.ceil(total / size))}
      </span>
      <button
        className="secondary-button"
        disabled={page * size >= total}
        onClick={() => change(page + 1)}
      >
        {t("next")}
      </button>
    </div>
  );
}
export function SeatIcon() {
  return (
    <svg viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <path
        d="M9 6h14v13H9zM7 19h18v5H7zM9 24v4m14-4v4M5 13v7m22-7v7"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
