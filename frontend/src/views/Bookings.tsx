import { useState } from "react";
import { api, query } from "../api/client";
import type { Booking, Page, User } from "../api/client";
import { formatBookingEnd, formatTime } from "../i18n";
import type { Language, T } from "../i18n";
import { useQuery } from "../hooks";
import {
  Empty,
  ErrorBanner,
  Loading,
  Modal,
  Pagination,
} from "../components/ui";

export function BookingList({
  items,
  t,
  language,
  cancel,
}: {
  items: Booking[];
  t: T;
  language: Language;
  cancel: (item: Booking) => void;
}) {
  return (
    <div className="booking-list">
      {items.map((item) => (
        <article className="booking-row" key={item.id}>
          <div className="booking-seat">
            <span>{t("seat")}</span>
            <strong>{item.seat_code}</strong>
          </div>
          <div className="booking-details">
            <h3>{item.room_name}</h3>
            <p>
              {item.business_date} · {formatTime(item.starts_at, language)}–
              {formatBookingEnd(item.ends_at, language)}
            </p>
            {item.username !== undefined && (
              <p className="small muted">
                {item.display_name || "—"} · {item.username || "—"}
              </p>
            )}
            {item.cancellation_reason && (
              <p className="small muted">
                {t("cancelReason")}：
                {item.cancellation_reason === "STUDENT_CANCELLED"
                  ? t("cancelled")
                  : item.cancellation_reason}
              </p>
            )}
          </div>
          <div className="booking-actions">
            <span className={`status-pill ${item.status.toLowerCase()}`}>
              {t(item.status)}
            </span>
            {item.can_cancel && (
              <button
                className="text-button danger"
                onClick={() => cancel(item)}
              >
                {t("cancelBooking")}
              </button>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}

export function CancelDialog({
  booking,
  user,
  t,
  language,
  close,
  changed,
}: {
  booking: Booking;
  user: User;
  t: T;
  language: Language;
  close: () => void;
  changed: () => void;
}) {
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  return (
    <Modal
      title={t("cancelBooking")}
      close={() => {
        if (!busy) close();
      }}
      t={t}
    >
      <p>{t("cancelHint")}</p>
      <div className="mini-ticket">
        <strong>
          {booking.room_name} · {booking.seat_code}
        </strong>
        <p>
          {booking.business_date} · {formatTime(booking.starts_at, language)}–
          {formatBookingEnd(booking.ends_at, language)}
        </p>
      </div>
      <form
        className="stack-form"
        onSubmit={async (e) => {
          e.preventDefault();
          if (busy) return;
          setBusy(true);
          setError(null);
          try {
            await api(`/bookings/${booking.id}/cancel`, {
              method: "POST",
              body: user.role === "ADMIN" ? { reason } : {},
            });
            changed();
            close();
          } catch (cause) {
            setError(cause);
          } finally {
            setBusy(false);
          }
        }}
      >
        {user.role === "ADMIN" && (
          <label>
            {t("reason")}
            <input
              required
              maxLength={240}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </label>
        )}
        <ErrorBanner error={error} t={t} />
        <button className="primary-button danger-button" disabled={busy}>
          {busy ? t("busy") : t("confirmCancel")}
        </button>
      </form>
    </Modal>
  );
}

export default function Bookings({
  user,
  t,
  language,
  revision,
  changed,
  onLogin,
}: {
  user: User | null;
  t: T;
  language: Language;
  revision: number;
  changed: () => void;
  onLogin: () => void;
}) {
  const [status, setStatus] = useState("");
  const [day, setDay] = useState("");
  const [page, setPage] = useState(1);
  const [nonce, setNonce] = useState(0);
  const [pending, setPending] = useState<Booking | null>(null);
  const result = useQuery<Page<Booking>>(
    user ? `/bookings?${query({ status, day, page })}` : null,
    revision + nonce,
  );
  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">{t("planEyebrow")}</p>
        <h1>{t("mine")}</h1>
        <p>{t("mineIntro")}</p>
      </header>
      {!user ? (
        <section className="panel">
          <Empty>{t("signInHint")}</Empty>
          <button className="primary-button" onClick={onLogin}>
            {t("login")}
          </button>
        </section>
      ) : (
        <section className="panel">
          <div className="compact-filters">
            <label>
              {t("status")}
              <select
                value={status}
                onChange={(e) => {
                  setStatus(e.target.value);
                  setPage(1);
                }}
              >
                <option value="">{t("all")}</option>
                {(
                  ["UPCOMING", "ONGOING", "COMPLETED", "CANCELLED"] as const
                ).map((x) => (
                  <option key={x} value={x}>
                    {t(x)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("bookingDate")}
              <input
                type="date"
                value={day}
                onChange={(e) => {
                  setDay(e.target.value);
                  setPage(1);
                }}
              />
            </label>
            <button
              className="text-button"
              onClick={() => {
                setStatus("");
                setDay("");
                setPage(1);
                setNonce((n) => n + 1);
              }}
            >
              {t("clear")}
            </button>
          </div>
          <ErrorBanner
            error={result.error}
            t={t}
            retry={() => setNonce((n) => n + 1)}
          />
          {result.loading && <Loading t={t} />}
          {result.data && (
            <>
              <BookingList
                items={result.data.items}
                t={t}
                language={language}
                cancel={setPending}
              />
              {result.data.items.length === 0 && (
                <Empty>{t("noBookings")}</Empty>
              )}
              <Pagination
                page={page}
                total={result.data.total}
                change={setPage}
                t={t}
              />
            </>
          )}
          <p className="form-hint">
            {t("retained")} · {t("timezone")}
          </p>
        </section>
      )}
      {pending && user && (
        <CancelDialog
          booking={pending}
          user={user}
          t={t}
          language={language}
          close={() => setPending(null)}
          changed={changed}
        />
      )}
    </>
  );
}
