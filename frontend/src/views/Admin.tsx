import { useState } from "react";
import type { ReactNode } from "react";
import { api, query } from "../api/client";
import type { Booking, Page, Policy, Room, Seat, User } from "../api/client";
import { actionText, formatTime } from "../i18n";
import type { Language, T } from "../i18n";
import { useQuery } from "../hooks";
import {
  Empty,
  ErrorBanner,
  Loading,
  Modal,
  Pagination,
} from "../components/ui";
import { BookingList, CancelDialog } from "./Bookings";
import { timeOptions } from "../time";

type Shared = {
  t: T;
  language: Language;
  revision: number;
  changed: () => void;
};
function ActionForm({
  children,
  save,
  done,
  t,
}: {
  children: ReactNode;
  save: (data: FormData) => Promise<unknown>;
  done: (result: unknown) => void;
  t: T;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  return (
    <form
      className="stack-form"
      onSubmit={async (event) => {
        event.preventDefault();
        if (busy) return;
        const data = new FormData(event.currentTarget);
        setBusy(true);
        setError(null);
        try {
          const result = await save(data);
          done(result);
        } catch (cause) {
          setError(cause);
        } finally {
          setBusy(false);
        }
      }}
    >
      {children}
      <ErrorBanner error={error} t={t} />
      <button className="primary-button" disabled={busy}>
        {busy ? t("busy") : t("save")}
      </button>
    </form>
  );
}
const value = (data: FormData, key: string) => String(data.get(key) || "");
function HourFields({
  t,
  opening = "08:00",
  closing = "22:00",
}: {
  t: T;
  opening?: string;
  closing?: string;
}) {
  return (
    <div className="form-grid">
      <label>
        {t("start")}
        <select name="opens_at" defaultValue={opening}>
          {timeOptions.slice(0, -1).map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
      </label>
      <label>
        {t("end")}
        <select name="closes_at" defaultValue={closing}>
          {timeOptions.slice(1).map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
      </label>
    </div>
  );
}
function Reason({ t }: { t: T }) {
  return (
    <label>
      {t("reason")}
      <input name="reason" required maxLength={240} />
    </label>
  );
}

function ResourceManager({
  t,
  revision,
  changed,
  policy,
}: Shared & { policy: Policy }) {
  const rooms = useQuery<{ items: Room[] }>("/admin/rooms", revision);
  const [chosen, setChosen] = useState<number | null>(null);
  const room =
    rooms.data?.items.find((x) => x.id === chosen) || rooms.data?.items[0];
  const seats = useQuery<{ items: Seat[] }>(
    room ? `/admin/rooms/${room.id}/seats` : null,
    revision,
  );
  const exceptions = useQuery<{
    items: {
      id: number;
      day: string;
      closed: boolean;
      opens_at: string;
      closes_at: string;
    }[];
  }>(room ? `/admin/opening-exceptions?room_id=${room.id}` : null, revision);
  const [roomEdit, setRoomEdit] = useState<Room | "new" | null>(null);
  const [seatEdit, setSeatEdit] = useState<Seat | "new" | null>(null);
  const [remove, setRemove] = useState<number | null>(null);
  const editingRoom = roomEdit && roomEdit !== "new" ? roomEdit : null;
  const editingSeat = seatEdit && seatEdit !== "new" ? seatEdit : null;
  return (
    <>
      <div className="admin-resource-layout">
        <section className="panel">
          <div className="section-heading">
            <h2>{t("spaces")}</h2>
            <button
              className="secondary-button"
              onClick={() => setRoomEdit("new")}
            >
              {t("newRoom")}
            </button>
          </div>
          <ErrorBanner error={rooms.error} t={t} retry={changed} />
          {rooms.loading && <Loading t={t} />}
          <div className="admin-space-list">
            {rooms.data?.items.map((x) => (
              <button
                key={x.id}
                className={room?.id === x.id ? "active" : ""}
                onClick={() => setChosen(x.id)}
              >
                <strong>{x.name}</strong>
                <span>
                  {x.capacity} · {x.enabled ? t("enabled") : t("disabled")}
                </span>
              </button>
            ))}
          </div>
        </section>
        <section className="panel">
          {room ? (
            <>
              <div className="section-heading">
                <h2>{room.name}</h2>
                <button
                  className="text-button"
                  onClick={() => setRoomEdit(room)}
                >
                  {t("editRoom")}
                </button>
              </div>
              <p className="muted">
                {room.campus} · {room.building} · {t("floor")} {room.floor}
              </p>
              <p>
                {t("opening")} {room.regular_opens_at}–{room.regular_closes_at}
              </p>
              <p className="form-hint">{t("changeHint")}</p>
              <div className="section-heading inset">
                <h3>{t("seats")}</h3>
                <button
                  className="secondary-button"
                  onClick={() => setSeatEdit("new")}
                >
                  {t("newSeat")}
                </button>
              </div>
              <ErrorBanner error={seats.error} t={t} />
              {seats.loading && <Loading t={t} />}
              <div className="admin-seats">
                {seats.data?.items.map((x) => (
                  <button
                    key={x.id}
                    className={!x.enabled ? "is-disabled" : ""}
                    onClick={() => setSeatEdit(x)}
                    aria-label={`${t("editSeat")} ${x.code}`}
                  >
                    <strong>{x.code}</strong>
                    <span>{x.enabled ? t("enabled") : t("disabled")}</span>
                  </button>
                ))}
              </div>
            </>
          ) : (
            <Empty>{t("emptyRooms")}</Empty>
          )}
        </section>
      </div>
      {room && (
        <div className="admin-resource-layout">
          <section className="panel">
            <h2>{t("dateExceptions")}</h2>
            <p className="muted small">{t("dateExceptionHint")}</p>
            <ActionForm
              key={`exception-${room.id}`}
              t={t}
              done={() => changed()}
              save={(data) =>
                api("/admin/opening-exceptions", {
                  method: "POST",
                  body: {
                    room_id: room.id,
                    day: value(data, "day"),
                    closed: data.has("closed"),
                    opens_at: value(data, "opens_at"),
                    closes_at: value(data, "closes_at"),
                    reason: value(data, "reason"),
                  },
                })
              }
            >
              <label>
                {t("bookingDate")}
                <input
                  type="date"
                  name="day"
                  required
                  defaultValue={policy.today}
                />
              </label>
              <label className="check-label">
                <input type="checkbox" name="closed" />
                {t("closed")}
              </label>
              <HourFields t={t} />
              <Reason t={t} />
            </ActionForm>
            <ErrorBanner error={exceptions.error} t={t} />
            <ul className="exception-list">
              {exceptions.data?.items.map((x) => (
                <li key={x.id}>
                  <span>
                    {x.day} ·{" "}
                    {x.closed ? t("closed") : `${x.opens_at}–${x.closes_at}`}
                  </span>
                  <button
                    className="text-button danger"
                    onClick={() => setRemove(x.id)}
                  >
                    {t("remove")}
                  </button>
                </li>
              ))}
            </ul>
          </section>
          <section className="panel">
            <h2>{t("policy")}</h2>
            <p className="muted small">{t("ruleHint")}</p>
            <ActionForm
              t={t}
              done={() => changed()}
              save={(data) =>
                api("/admin/policy", {
                  method: "PUT",
                  body: {
                    advance_days: Number(value(data, "advance_days")),
                    reason: value(data, "reason"),
                  },
                })
              }
            >
              <label>
                {t("advanceDays")}
                <select name="advance_days" defaultValue={policy.advance_days}>
                  {Array.from({ length: 7 }, (_, i) => (
                    <option key={i} value={i + 1}>
                      {i + 1} {t("days")}
                    </option>
                  ))}
                </select>
              </label>
              <Reason t={t} />
            </ActionForm>
          </section>
        </div>
      )}
      {roomEdit && (
        <Modal
          t={t}
          title={editingRoom ? t("editRoom") : t("newRoom")}
          close={() => setRoomEdit(null)}
        >
          <p className="form-hint">{t("changeHint")}</p>
          <ActionForm
            t={t}
            done={(result) => {
              const updated = result as Room;
              setChosen(updated.id);
              setRoomEdit(null);
              changed();
            }}
            save={(data) =>
              api(`/admin/rooms${editingRoom ? `/${editingRoom.id}` : ""}`, {
                method: editingRoom ? "PUT" : "POST",
                body: {
                  name: value(data, "name"),
                  campus: value(data, "campus"),
                  building: value(data, "building"),
                  floor: Number(value(data, "floor")),
                  kind: value(data, "kind"),
                  description: value(data, "description"),
                  enabled: data.has("enabled"),
                  opens_at: value(data, "opens_at"),
                  closes_at: value(data, "closes_at"),
                  reason: value(data, "reason"),
                },
              })
            }
          >
            <label>
              {t("roomName")}
              <input
                name="name"
                required
                maxLength={80}
                defaultValue={editingRoom?.name}
              />
            </label>
            <div className="form-grid">
              <label>
                {t("campus")}
                <input
                  name="campus"
                  required
                  maxLength={60}
                  defaultValue={editingRoom?.campus}
                />
              </label>
              <label>
                {t("building")}
                <input
                  name="building"
                  required
                  maxLength={60}
                  defaultValue={editingRoom?.building}
                />
              </label>
            </div>
            <div className="form-grid">
              <label>
                {t("floor")}
                <input
                  type="number"
                  name="floor"
                  required
                  min={-5}
                  max={100}
                  defaultValue={editingRoom?.floor ?? 1}
                />
              </label>
              <label>
                {t("kind")}
                <select
                  name="kind"
                  defaultValue={editingRoom?.kind || "STUDY_ROOM"}
                >
                  <option value="STUDY_ROOM">{t("studyRoom")}</option>
                  <option value="CLASSROOM">{t("classroom")}</option>
                </select>
              </label>
            </div>
            <label>
              {t("description")}
              <input
                name="description"
                maxLength={240}
                defaultValue={editingRoom?.description}
              />
            </label>
            <HourFields
              t={t}
              opening={editingRoom?.regular_opens_at}
              closing={editingRoom?.regular_closes_at}
            />
            <label className="check-label">
              <input
                type="checkbox"
                name="enabled"
                defaultChecked={editingRoom?.enabled ?? true}
              />
              {t("enabled")}
            </label>
            <Reason t={t} />
          </ActionForm>
        </Modal>
      )}
      {seatEdit && room && (
        <Modal
          t={t}
          title={editingSeat ? t("editSeat") : t("newSeat")}
          close={() => setSeatEdit(null)}
        >
          <ActionForm
            t={t}
            done={() => {
              setSeatEdit(null);
              changed();
            }}
            save={(data) =>
              api(`/admin/seats${editingSeat ? `/${editingSeat.id}` : ""}`, {
                method: editingSeat ? "PUT" : "POST",
                body: {
                  room_id: room.id,
                  code: value(data, "code"),
                  enabled: data.has("enabled"),
                  reason: value(data, "reason"),
                },
              })
            }
          >
            <label>
              {t("seatCode")}
              <input
                name="code"
                required
                maxLength={24}
                defaultValue={editingSeat?.code}
              />
            </label>
            <label className="check-label">
              <input
                type="checkbox"
                name="enabled"
                defaultChecked={editingSeat?.enabled ?? true}
              />
              {t("enabled")}
            </label>
            <p className="form-hint">{t("changeHint")}</p>
            <Reason t={t} />
          </ActionForm>
        </Modal>
      )}
      {remove !== null && (
        <Modal t={t} title={t("confirmChange")} close={() => setRemove(null)}>
          <ActionForm
            t={t}
            done={() => {
              setRemove(null);
              changed();
            }}
            save={(data) =>
              api(`/admin/opening-exceptions/${remove}/remove`, {
                method: "POST",
                body: { reason: value(data, "reason") },
              })
            }
          >
            <p>{t("dateExceptionHint")}</p>
            <Reason t={t} />
          </ActionForm>
        </Modal>
      )}
    </>
  );
}

function Records({
  t,
  language,
  revision,
  changed,
  policy,
  user,
}: Shared & { policy: Policy; user: User }) {
  const [day, setDay] = useState(policy.today);
  const [username, setUsername] = useState("");
  const [status, setStatus] = useState("");
  const [roomId, setRoomId] = useState("");
  const [seatId, setSeatId] = useState("");
  const [page, setPage] = useState(1);
  const [pending, setPending] = useState<Booking | null>(null);
  const stats = useQuery<{
    created: number;
    cancelled: number;
    active: number;
    as_of: string;
  }>(`/admin/statistics?${query({ day })}`, revision);
  const rooms = useQuery<{ items: Room[] }>("/admin/rooms", revision);
  const result = useQuery<Page<Booking>>(
    `/admin/bookings?${query({ day, username, status, room_id: roomId, seat_id: seatId, page })}`,
    revision,
  );
  return (
    <>
      <section className="panel">
        <div className="section-heading">
          <h2>{t("records")}</h2>
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
        </div>
        <ErrorBanner error={stats.error} t={t} />
        {stats.loading && <Loading t={t} />}
        {stats.data && (
          <>
            <div className="stat-grid">
              {(["created", "cancelled", "active"] as const).map((key) => (
                <div className="stat" key={key}>
                  <span>{t(key === "cancelled" ? "cancelledCount" : key)}</span>
                  <strong>{stats.data?.[key]}</strong>
                </div>
              ))}
            </div>
            <p className="form-hint">
              {t("snapshot")} {formatTime(stats.data.as_of, language, true)} ·{" "}
              {t("statsHint")}
            </p>
          </>
        )}
      </section>
      <section className="panel">
        <div className="compact-filters">
          <label>
            {t("username")}
            <input
              value={username}
              maxLength={32}
              onChange={(e) => {
                setUsername(e.target.value);
                setPage(1);
              }}
            />
          </label>
          <label>
            {t("spaces")}
            <select
              value={roomId}
              onChange={(e) => {
                setRoomId(e.target.value);
                setPage(1);
              }}
            >
              <option value="">{t("all")}</option>
              {rooms.data?.items.map((x) => (
                <option key={x.id} value={x.id}>
                  {x.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("seat")} ID
            <input
              type="number"
              min={1}
              value={seatId}
              onChange={(e) => {
                setSeatId(e.target.value);
                setPage(1);
              }}
            />
          </label>
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
              {(["UPCOMING", "ONGOING", "COMPLETED", "CANCELLED"] as const).map(
                (x) => (
                  <option key={x} value={x}>
                    {t(x)}
                  </option>
                ),
              )}
            </select>
          </label>
        </div>
        <ErrorBanner error={result.error} t={t} retry={changed} />
        {result.loading && <Loading t={t} />}
        {result.data && (
          <>
            <BookingList
              items={result.data.items}
              t={t}
              language={language}
              cancel={setPending}
            />
            {result.data.items.length === 0 && <Empty>{t("noBookings")}</Empty>}
            <Pagination
              page={page}
              total={result.data.total}
              change={setPage}
              t={t}
            />
          </>
        )}
      </section>
      {pending && (
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

function Users({ t, revision, changed }: Shared) {
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [editing, setEditing] = useState<User | null>(null);
  const result = useQuery<Page<User>>(
    `/admin/users?${query({ q, page })}`,
    revision,
  );
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>{t("users")}</h2>
        <label>
          {t("username")}
          <input
            maxLength={32}
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setPage(1);
            }}
          />
        </label>
      </div>
      <p className="form-hint">{t("userHint")}</p>
      <ErrorBanner error={result.error} t={t} retry={changed} />
      {result.loading && <Loading t={t} />}
      <div className="user-list">
        {result.data?.items.map((x) => (
          <article key={x.id}>
            <span className="avatar">{x.display_name.slice(0, 1)}</span>
            <div>
              <strong>{x.display_name}</strong>
              <p>{x.username}</p>
            </div>
            <span className="status-pill">
              {t(x.role)} · {x.enabled ? t("enabled") : t("disabled")}
            </span>
            <button className="text-button" onClick={() => setEditing(x)}>
              {t("edit")}
            </button>
          </article>
        ))}
      </div>
      {result.data?.items.length === 0 && <Empty>{t("noUsers")}</Empty>}
      <Pagination
        page={page}
        total={result.data?.total || 0}
        change={setPage}
        t={t}
      />
      {editing && (
        <Modal
          t={t}
          title={`${t("edit")} · ${editing.username}`}
          close={() => setEditing(null)}
        >
          <ActionForm
            t={t}
            done={() => {
              setEditing(null);
              changed();
            }}
            save={(data) =>
              api(`/admin/users/${editing.id}`, {
                method: "PUT",
                body: {
                  role: value(data, "role"),
                  enabled: data.has("enabled"),
                  reason: value(data, "reason"),
                },
              })
            }
          >
            <p className="muted">{t("userHint")}</p>
            <label>
              {t("role")}
              <select name="role" defaultValue={editing.role}>
                <option value="STUDENT">{t("STUDENT")}</option>
                <option value="ADMIN">{t("ADMIN")}</option>
              </select>
            </label>
            <label className="check-label">
              <input
                type="checkbox"
                name="enabled"
                defaultChecked={editing.enabled}
              />
              {t("enabled")}
            </label>
            <Reason t={t} />
          </ActionForm>
        </Modal>
      )}
    </section>
  );
}

function Audit({ t, language, revision }: Shared) {
  const [page, setPage] = useState(1);
  const result = useQuery<
    Page<{
      id: number;
      actor_id: number | null;
      action: string;
      target_type: string;
      target_id: number;
      created_at: string;
    }>
  >(`/admin/audit?${query({ page })}`, revision);
  return (
    <section className="panel">
      <h2>{t("audit")}</h2>
      <ErrorBanner error={result.error} t={t} />
      {result.loading && <Loading t={t} />}
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>{t("time")}</th>
              <th>{t("actor")}</th>
              <th>{t("action")}</th>
              <th>{t("target")}</th>
            </tr>
          </thead>
          <tbody>
            {result.data?.items.map((x) => (
              <tr key={x.id}>
                <td>{formatTime(x.created_at, language, true)}</td>
                <td>{x.actor_id ?? "—"}</td>
                <td>{actionText(x.action, t)}</td>
                <td>
                  {t(
                    x.target_type === "room"
                      ? "spaces"
                      : x.target_type === "seat"
                        ? "seat"
                        : x.target_type === "user"
                          ? "users"
                          : x.target_type === "policy"
                            ? "policy"
                            : "mine",
                  )}{" "}
                  #{x.target_id}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination
        page={page}
        total={result.data?.total || 0}
        change={setPage}
        t={t}
      />
    </section>
  );
}

export default function Admin(props: Shared & { policy: Policy; user: User }) {
  const [tab, setTab] = useState<"resources" | "records" | "users" | "audit">(
    "resources",
  );
  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">{props.t("adminEyebrow")}</p>
        <h1>{props.t("admin")}</h1>
        <p>{props.t("adminIntro")}</p>
      </header>
      <div className="admin-tabs" role="tablist">
        {(["resources", "records", "users", "audit"] as const).map((key) => (
          <button
            role="tab"
            aria-selected={tab === key}
            key={key}
            onClick={() => setTab(key)}
          >
            {props.t(key)}
          </button>
        ))}
      </div>
      {tab === "resources" && <ResourceManager {...props} />}
      {tab === "records" && <Records {...props} />}
      {tab === "users" && <Users {...props} />}
      {tab === "audit" && <Audit {...props} />}
    </>
  );
}
