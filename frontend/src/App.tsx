import { useEffect, useRef, useState } from "react";
import { api } from "./api/client";
import type { Policy, User } from "./api/client";
import { useQuery } from "./hooks";
import { translator } from "./i18n";
import type { Language, Message } from "./i18n";
import { ErrorBanner, Loading } from "./components/ui";
import Auth from "./views/Auth";
import Rooms from "./views/Rooms";
import Bookings from "./views/Bookings";
import Admin from "./views/Admin";

type View = "find" | "mine" | "admin";
export default function App() {
  const [language, setLanguage] = useState<Language>("zh-CN");
  const [user, setUser] = useState<User | null>(null);
  const [view, setView] = useState<View>("find");
  const [auth, setAuth] = useState(false);
  const [revision, setRevision] = useState(0);
  const [notice, setNotice] = useState<Message | null>(null);
  const [error, setError] = useState<unknown>(null);
  const sessionEpoch = useRef(0);
  const t = translator(language);
  const policy = useQuery<Policy>("/policy", revision);
  const currentPolicy = policy.data || policy.previousData;
  useEffect(() => {
    document.documentElement.lang = language;
    document.title = `StudySpace · ${translator(language)("find")}`;
  }, [language]);
  useEffect(() => {
    const controller = new AbortController();
    const epoch = sessionEpoch.current;
    api<User>("/auth/me", {
      signal: controller.signal,
      quietUnauthorized: true,
    }).then(
      (value) => {
        if (!controller.signal.aborted && sessionEpoch.current === epoch)
          setUser(value);
      },
      () => {
        /* anonymous browsing remains available */
      },
    );
    const endSession = () => {
      sessionEpoch.current++;
      setUser(null);
      setView("find");
    };
    window.addEventListener("studyspace:session-ended", endSession);
    return () => {
      controller.abort();
      window.removeEventListener("studyspace:session-ended", endSession);
    };
  }, []);
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(null), 6000);
    return () => clearTimeout(timer);
  }, [notice]);
  function mutation(message: Message = "saved") {
    setRevision((n) => n + 1);
    setNotice(message);
  }
  async function logout() {
    setError(null);
    try {
      await api("/auth/logout", { method: "POST" });
      sessionEpoch.current++;
      setUser(null);
      setView("find");
    } catch (cause) {
      setError(cause);
    }
  }
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#main" aria-label="StudySpace">
          <span className="brand-symbol" aria-hidden="true">
            s<span>.</span>
          </span>
          <span>
            StudySpace<small>A LITTLE ROOM TO THINK</small>
          </span>
        </a>
        <div className="workspace-label">{t("local")}</div>
        <nav aria-label="StudySpace">
          <button
            className={view === "find" ? "active" : ""}
            onClick={() => setView("find")}
            aria-current={view === "find" ? "page" : undefined}
          >
            <span aria-hidden="true">⌑</span>
            {t("find")}
          </button>
          <button
            className={view === "mine" ? "active" : ""}
            onClick={() => setView("mine")}
            aria-current={view === "mine" ? "page" : undefined}
          >
            <span aria-hidden="true">▤</span>
            {t("mine")}
          </button>
          {user?.role === "ADMIN" && (
            <button
              className={view === "admin" ? "active" : ""}
              onClick={() => setView("admin")}
            >
              <span aria-hidden="true">⚑</span>
              {t("admin")}
            </button>
          )}
        </nav>
        <div className="sidebar-note">
          <span className="tiny-dot" />
          {t("local")}
          <p>{t("timezone")}</p>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <span className="breadcrumb">
            StudySpace <span aria-hidden="true">/</span>{" "}
            {t(view === "find" ? "find" : view === "mine" ? "mine" : "admin")}
          </span>
          <div className="topbar-actions">
            <div
              className="language-switch"
              role="group"
              aria-label="Language / Язык / 语言"
            >
              {(["zh-CN", "ru-RU", "en-US"] as const).map((lang, i) => (
                <button
                  key={lang}
                  onClick={() => setLanguage(lang)}
                  aria-pressed={language === lang}
                >
                  {["中文", "Русский", "English"][i]}
                </button>
              ))}
            </div>
            {user ? (
              <div className="account">
                <span className="avatar" aria-hidden="true">
                  {user.display_name.slice(0, 1)}
                </span>
                <span className="account-name">{user.display_name}</span>
                <button className="text-button" onClick={logout}>
                  {t("logout")}
                </button>
              </div>
            ) : (
              <button className="header-login" onClick={() => setAuth(true)}>
                {t("login")}
              </button>
            )}
          </div>
        </header>
        <main id="main">
          <div className="local-note">
            <span className="tiny-dot" />
            {t("privacy")}
          </div>
          <ErrorBanner error={error} t={t} />
          {notice && (
            <div className="toast" role="status">
              <span aria-hidden="true">✓ </span>
              <span>{t(notice)}</span>
            </div>
          )}
          {view === "find" && (
            <>
              <ErrorBanner
                error={policy.error}
                t={t}
                retry={() => setRevision((n) => n + 1)}
              />
              {policy.loading && !currentPolicy && <Loading t={t} />}
              {currentPolicy && (
                <Rooms
                  policy={currentPolicy}
                  user={user}
                  language={language}
                  t={t}
                  revision={revision}
                  onLogin={() => setAuth(true)}
                  onBooked={() => mutation("bookingSuccess")}
                />
              )}
            </>
          )}
          {view === "mine" && (
            <Bookings
              user={user}
              language={language}
              t={t}
              revision={revision}
              changed={() => mutation("cancelled")}
              onLogin={() => setAuth(true)}
            />
          )}
          {view === "admin" && user?.role === "ADMIN" && currentPolicy && (
            <Admin
              user={user}
              policy={currentPolicy}
              language={language}
              t={t}
              revision={revision}
              changed={() => mutation()}
            />
          )}
        </main>
        <footer className="app-footer">
          <span>StudySpace</span>
          <span>
            {t("local")} · {t("timezone")}
          </span>
        </footer>
      </div>
      {auth && (
        <Auth
          t={t}
          close={() => setAuth(false)}
          signedIn={(value) => {
            sessionEpoch.current++;
            setUser(value);
            setAuth(false);
            setError(null);
          }}
        />
      )}
    </div>
  );
}
