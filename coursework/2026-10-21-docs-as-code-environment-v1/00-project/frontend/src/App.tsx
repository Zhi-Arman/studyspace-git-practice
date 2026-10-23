import { useEffect, useState } from 'react';
import { Alert, Button, ConfigProvider, Tag } from 'antd';
import enUS from 'antd/locale/en_US';
import ruRU from 'antd/locale/ru_RU';
import zhCN from 'antd/locale/zh_CN';
import { getHealth, HealthError } from './api/health';
import type { HealthErrorCode } from './api/health';
import { content } from './content';
import type { Language } from './content';

type Connection = { status: 'checking' | 'connected' } | { status: 'failed'; code: HealthErrorCode };

export default function App() {
  const [language, setLanguage] = useState<Language>('zh-CN');
  const [attempt, setAttempt] = useState(0);
  const [connection, setConnection] = useState<Connection>({ status: 'checking' });
  const copy = content[language];

  useEffect(() => {
    document.documentElement.lang = language;
    document.title = `StudySpace — ${content[language].title}`;
  }, [language]);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    void getHealth({ signal: controller.signal }).then(
      () => { if (active) setConnection({ status: 'connected' }); },
      (error: unknown) => {
        if (active) setConnection({ status: 'failed', code: error instanceof HealthError ? error.code : 'network' });
      },
    );
    return () => {
      active = false;
      controller.abort();
    };
  }, [attempt]);

  const retry = () => {
    setConnection({ status: 'checking' });
    setAttempt((previous) => previous + 1);
  };

  return (
    <ConfigProvider locale={{ 'zh-CN': zhCN, 'ru-RU': ruRU, 'en-US': enUS }[language]} theme={{
      token: { colorPrimary: '#214b3d', borderRadius: 8, fontFamily: "'PingFang SC', 'Segoe UI', sans-serif" },
    }}>
      <div className="page">
        <header className="site-header">
          <a className="brand" href="#top" aria-label="StudySpace">
            <img src="/favicon.svg" alt="" width="34" height="34" />
            <span>StudySpace</span>
          </a>
          <div className="language-switch" role="group" aria-label="Language / Язык / 语言">
            <Button type={language === 'zh-CN' ? 'primary' : 'text'} aria-label="中文" aria-pressed={language === 'zh-CN'} onClick={() => setLanguage('zh-CN')}>中文</Button>
            <Button type={language === 'ru-RU' ? 'primary' : 'text'} aria-label="Русский" aria-pressed={language === 'ru-RU'} onClick={() => setLanguage('ru-RU')}>Русский</Button>
            <Button type={language === 'en-US' ? 'primary' : 'text'} aria-label="English" aria-pressed={language === 'en-US'} onClick={() => setLanguage('en-US')}>English</Button>
          </div>
        </header>

        <main id="top">
          <section className="hero" aria-labelledby="project-title">
            <div className="hero-meta"><span>{copy.projectType}</span><Tag color="default">v0.1.0 · {copy.draft}</Tag></div>
            <p className="wordmark" aria-hidden="true">StudySpace<span>.</span></p>
            <h1 id="project-title">{copy.title}</h1>
            <p className="introduction">{copy.introduction}</p>
            <Alert message={copy.scopeNotice} type="info" showIcon className="scope-notice" />
          </section>

          <section className="foundation section" aria-labelledby="foundation-title">
            <div className="section-intro">
              <p className="eyebrow">{copy.foundationLabel}</p>
              <h2 id="foundation-title">{copy.foundationTitle}</h2>
              <p>{copy.foundationDescription}</p>
              <ol className="architecture" aria-label="Technology / Технологии / 技术架构">
                <li><b>React + TypeScript</b><span>Vite · Ant Design</span></li>
                <li><b>FastAPI</b><span>Python · Pydantic</span></li>
                <li><b>SQLAlchemy</b><span>SQLite → PostgreSQL</span></li>
              </ol>
            </div>
            <div className="connection-panel">
              <span className="small-label">{copy.connection}</span>
              <div className={`connection-state ${connection.status}`} role="status" aria-live="polite">
                <span className="status-dot" aria-hidden="true" />
                <strong>{copy[connection.status]}</strong>
              </div>
              <p className="connection-detail">{connection.status === 'connected' ? copy.contract : connection.status === 'failed' ? copy.error[connection.code] : 'GET /api/v1/health'}</p>
              <div className="connection-actions">
                <Button onClick={retry} loading={connection.status === 'checking'}>{copy.retry}</Button>
                <Button type="link" href="/api/v1/docs" target="_blank" rel="noopener noreferrer">{copy.apiDocs} ↗</Button>
              </div>
              <p className="boundary-note">{copy.healthBoundary}</p>
            </div>
          </section>

          <section className="section roadmap" aria-labelledby="roadmap-title">
            <div className="roadmap-heading">
              <div><p className="eyebrow">{copy.roadmapLabel}</p><h2 id="roadmap-title">{copy.roadmapTitle}</h2></div>
              <span className="planned-label">{copy.planned}</span>
            </div>
            <div className="role-grid">
              {[{ name: copy.student, number: 'A', items: copy.studentItems }, { name: copy.administrator, number: 'B', items: copy.adminItems }].map((role) => (
                <article className="role-panel" key={role.number}>
                  <div className="role-heading"><span className="role-number" aria-hidden="true">{role.number}</span><h3>{role.name}</h3></div>
                  <ul>{role.items.map((item) => <li key={item}>{item}</li>)}</ul>
                </article>
              ))}
            </div>
            <p className="extension-note">{copy.extension}</p>
          </section>
        </main>
        <footer><span>StudySpace</span><p>{copy.footer}</p></footer>
      </div>
    </ConfigProvider>
  );
}
