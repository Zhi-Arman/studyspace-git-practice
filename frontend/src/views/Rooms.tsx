import { timeOptions } from "../time";
import { useState } from "react";
import type { FormEvent } from "react";
import { api, query } from "../api/client";
import type {
  Booking,
  Page,
  Policy,
  Room,
  SeatResult,
  User,
} from "../api/client";
import { addDays, formatBookingEnd, formatTime } from "../i18n";
import type { Language, T } from "../i18n";
import { useQuery } from "../hooks";
import {
  Empty,
  ErrorBanner,
  Loading,
  Modal,
  Pagination,
  SeatIcon,
} from "../components/ui";

function initialInterval(policy: Policy) {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Shanghai",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(new Date(policy.server_now || Date.now()));
  const minute =
    Number(parts.find((x) => x.type === "hour")?.value || 0) * 60 +
    Number(parts.find((x) => x.type === "minute")?.value || 0);
  const next = Math.max(480, Math.ceil((minute + 1) / 30) * 30);
  const tomorrow = next + 60 > 1320;
  const start =
    tomorrow && policy.advance_days > 1 ? 540 : Math.min(next, 1410);
  const end = Math.min(start + 60, start < 1320 ? 1320 : 1440);
  return {
    day:
      tomorrow && policy.advance_days > 1
        ? addDays(policy.today, 1)
        : policy.today,
    start: timeOptions[start / 30],
    end: timeOptions[end / 30],
  };
}

export default function Rooms({
  policy,
  user,
  t,
  language,
  revision,
  onLogin,
  onBooked,
}: {
  policy: Policy;
  user: User | null;
  t: T;
  language: Language;
  revision: number;
  onLogin: () => void;
  onBooked: () => void;
}) {
  const [initial] = useState(() => initialInterval(policy));
  const [day, setDay] = useState(initial.day);
  const [start, setStart] = useState(initial.start);
  const [end, setEnd] = useState(initial.end);
  const [filters, setFilters] = useState({
    campus: "",
    building: "",
    floor: "",
    kind: "",
  });
  const [applied, setApplied] = useState(filters);
  const [page, setPage] = useState(1);
  const [nonce, setNonce] = useState(0);
  const [chosenRoom, setChosenRoom] = useState<number | null>(null);
  const [selection, setSelection] = useState<{
    key: string;
    id: number;
  } | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const result = useQuery<Page<Room>>(
    `/rooms?${query({ ...applied, day, page })}`,
    revision + nonce,
  );
  const room =
    result.data?.items.find((x) => x.id === chosenRoom) ||
    result.data?.items[0];
  const interval = {
    starts_at: `${day}T${start}:00+08:00`,
    ends_at:
      end === "24:00"
        ? `${addDays(day, 1)}T00:00:00+08:00`
        : `${day}T${end}:00+08:00`,
  };
  const rangeKey = `${room?.id}|${day}|${start}|${end}`;
  const seatResult = useQuery<SeatResult>(
    room ? `/rooms/${room.id}/seats?${query(interval)}` : null,
    revision + nonce,
  );
  const seat =
    selection?.key === rangeKey
      ? seatResult.data?.items.find((x) => x.id === selection.id && x.available)
      : undefined;
  async function reserve() {
    if (!seat || busy) return;
    setBusy(true);
    setError(null);
    try {
      await api<Booking>("/bookings", {
        method: "POST",
        body: { seat_id: seat.id, ...interval },
      });
      setConfirming(false);
      setSelection(null);
      onBooked();
    } catch (cause) {
      setError(cause);
    } finally {
      setBusy(false);
    }
  }
  function search(event: FormEvent) {
    event.preventDefault();
    setApplied(filters);
    setPage(1);
    setNonce((n) => n + 1);
    setError(null);
  }
  return (
    <>
      <section className="hero-panel">
        <div>
          <p className="eyebrow">{t("eyebrow")}</p>
          <h1>{t("headline")}</h1>
          <p className="hero-copy">{t("intro")}</p>
        </div>
        <div className="hero-art" aria-hidden="true">
          <span className="art-window" />
          <span className="art-book">
            S<span>STUDY / SPACE</span>
          </span>
          <span className="art-cup" />
        </div>
      </section>
      <form className="search-panel" onSubmit={search}>
        <div className="time-fields">
          <label>
            {t("bookingDate")}
            <input
              type="date"
              required
              min={policy.today}
              max={addDays(policy.today, policy.advance_days - 1)}
              value={day}
              onChange={(e) => setDay(e.target.value)}
            />
          </label>
          <label>
            {t("start")}
            <select value={start} onChange={(e) => setStart(e.target.value)}>
              {timeOptions.slice(0, -1).map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </label>
          <span className="time-arrow" aria-hidden="true">
            →
          </span>
          <label>
            {t("end")}
            <select value={end} onChange={(e) => setEnd(e.target.value)}>
              {timeOptions.slice(1).map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </label>
          <button className="primary-button search-button">
            {t("search")} <span aria-hidden="true">↗</span>
          </button>
        </div>
        <div className="filter-fields">
          <label>
            {t("campus")}
            <input
              value={filters.campus}
              onChange={(e) =>
                setFilters({ ...filters, campus: e.target.value })
              }
              maxLength={60}
            />
          </label>
          <label>
            {t("building")}
            <input
              value={filters.building}
              onChange={(e) =>
                setFilters({ ...filters, building: e.target.value })
              }
              maxLength={60}
            />
          </label>
          <label>
            {t("floor")}
            <input
              type="number"
              min={-5}
              max={100}
              value={filters.floor}
              onChange={(e) =>
                setFilters({ ...filters, floor: e.target.value })
              }
            />
          </label>
          <label>
            {t("kind")}
            <select
              value={filters.kind}
              onChange={(e) => setFilters({ ...filters, kind: e.target.value })}
            >
              <option value="">{t("all")}</option>
              <option value="STUDY_ROOM">{t("studyRoom")}</option>
              <option value="CLASSROOM">{t("classroom")}</option>
            </select>
          </label>
        </div>
        <p className="form-hint">
          {t("timezone")} · {policy.advance_days} {t("days")} · 30 min
        </p>
      </form>
      <div className="booking-layout">
        <section className="space-list">
          <div className="section-heading">
            <div>
              <span className="section-number">01</span>
              <h2>{t("spaces")}</h2>
            </div>
            <span className="count-badge">{result.data?.total ?? "—"}</span>
          </div>
          <p className="muted small">{t("spacesHint")}</p>
          <ErrorBanner
            error={result.error}
            t={t}
            retry={() => setNonce((n) => n + 1)}
          />
          {result.loading && <Loading t={t} />}
          {result.data?.items.map((x) => (
            <button
              key={x.id}
              type="button"
              className={`room-card ${room?.id === x.id ? "active" : ""}`}
              aria-pressed={room?.id === x.id}
              onClick={() => {
                setChosenRoom(x.id);
                setError(null);
              }}
            >
              <div className="room-card-top">
                <span className="space-type">
                  {t(x.kind === "CLASSROOM" ? "classroom" : "studyRoom")}
                </span>
                <span aria-hidden="true">↗</span>
              </div>
              <h3>{x.name}</h3>
              <p>
                {x.building} · {t("floor")} {x.floor}
              </p>
              <div className="room-card-bottom">
                <span>
                  <SeatIcon /> {t("capacity")} {x.capacity}
                </span>
                <span>
                  {x.closed ? t("closed") : `${x.opens_at}–${x.closes_at}`}
                </span>
              </div>
            </button>
          ))}
          {result.data?.items.length === 0 && <Empty>{t("emptyRooms")}</Empty>}
          <Pagination
            page={page}
            total={result.data?.total || 0}
            change={setPage}
            t={t}
          />
        </section>
        <section className="seat-panel">
          <div className="section-heading">
            <div>
              <span className="section-number">02</span>
              <h2>{t("seats")}</h2>
            </div>
          </div>
          <div className="seat-legend">
            <span>
              <i className="legend-dot free" />
              {t("available")}
            </span>
            <span>
              <i className="legend-dot chosen" />
              {t("selected")}
            </span>
            <span>
              <i className="legend-dot taken" />
              {t("unavailable")}
            </span>
          </div>
          <ErrorBanner
            error={seatResult.error}
            t={t}
            retry={() => setNonce((n) => n + 1)}
          />
          {seatResult.loading && <Loading t={t} />}
          {seatResult.data && (
            <>
              <div className="seat-room-label">
                <span>{room?.name}</span>
                <span className="window-mark" aria-hidden="true">
                  ▱ ▱ ▱
                </span>
              </div>
              <div className="seat-grid">
                {seatResult.data.items.map((x) => (
                  <button
                    className={`seat ${seat?.id === x.id ? "chosen" : ""}`}
                    key={x.id}
                    disabled={!x.available}
                    aria-pressed={seat?.id === x.id}
                    aria-label={`${t("seat")} ${x.code}, ${t(x.available ? "available" : "unavailable")}`}
                    onClick={() => {
                      setSelection({ id: x.id, key: rangeKey });
                      setError(null);
                    }}
                  >
                    <SeatIcon />
                    <strong>{x.code}</strong>
                  </button>
                ))}
              </div>
              {!seatResult.data.items.length && (
                <Empty>{t("emptySeats")}</Empty>
              )}
              {seatResult.data.items.length > 0 &&
                !seatResult.data.items.some((x) => x.available) && (
                  <p className="info-banner">{t("outsideHours")}</p>
                )}
            </>
          )}
          <div className="selection-summary">
            <div>
              <span className="eyebrow">
                {seat ? t("selected") : t("seat")}
              </span>
              <strong>
                {seat ? `${room?.name} · ${seat.code}` : t("chooseSeat")}
              </strong>
              <p>
                {day} · {start}–{end}
              </p>
            </div>
            <button
              className="primary-button"
              disabled={!seat || user?.role === "ADMIN"}
              onClick={() => {
                setError(null);
                if (!user) onLogin();
                else setConfirming(true);
              }}
            >
              {user ? t("reserve") : t("loginToBook")}
            </button>
          </div>
          {user?.role === "ADMIN" && (
            <p className="form-hint">{t("studentOnly")}</p>
          )}
          <p className="rule-note">{t("ruleHint")}</p>
        </section>
      </div>
      {confirming && seat && (
        <Modal
          title={t("reviewBooking")}
          t={t}
          close={() => {
            if (!busy) setConfirming(false);
          }}
        >
          <div className="confirmation-ticket">
            <p>{room?.name}</p>
            <strong>{seat.code}</strong>
            <p>{day}</p>
            <p>
              {formatTime(interval.starts_at, language)}–
              {formatBookingEnd(interval.ends_at, language)}
            </p>
            <small>{t("timezone")}</small>
          </div>
          <ErrorBanner error={error} t={t} />
          <button
            className="primary-button full"
            disabled={busy}
            onClick={reserve}
          >
            {busy ? t("busy") : t("confirmBooking")}
          </button>
        </Modal>
      )}
    </>
  );
}
