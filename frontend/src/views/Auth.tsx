import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api/client";
import type { User } from "../api/client";
import type { T } from "../i18n";
import { ErrorBanner, Modal } from "../components/ui";

export default function Auth({
  t,
  close,
  signedIn,
}: {
  t: T;
  close: () => void;
  signedIn: (user: User) => void;
}) {
  const [registering, setRegistering] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      if (registering)
        await api<User>("/auth/register", {
          method: "POST",
          body: { username, display_name: name, password },
        });
      const user = await api<User>("/auth/login", {
        method: "POST",
        body: { username, password },
      });
      signedIn(user);
    } catch (cause) {
      setError(cause);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal t={t} title={registering ? t("register") : t("login")} close={close}>
      <p className="muted">{t("privacy")}</p>
      <form onSubmit={submit} className="stack-form">
        <label>
          {t("username")}
          <input
            autoComplete="username"
            required
            minLength={3}
            maxLength={32}
            pattern="[A-Za-z0-9_]+"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </label>
        {registering && (
          <label>
            {t("displayName")}
            <input
              autoComplete="nickname"
              required
              maxLength={60}
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </label>
        )}
        <label>
          {t("password")}
          <input
            type="password"
            autoComplete={registering ? "new-password" : "current-password"}
            required
            minLength={registering ? 10 : 1}
            maxLength={128}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <ErrorBanner error={error} t={t} />
        <button className="primary-button full" disabled={busy}>
          {busy ? t("busy") : registering ? t("createAccount") : t("login")}
        </button>
      </form>
      <p className="form-hint">{t("accountHint")}</p>
      <button
        className="text-button full"
        disabled={busy}
        onClick={() => {
          setRegistering(!registering);
          setError(null);
        }}
      >
        {registering ? t("login") : t("register")}
      </button>
    </Modal>
  );
}
