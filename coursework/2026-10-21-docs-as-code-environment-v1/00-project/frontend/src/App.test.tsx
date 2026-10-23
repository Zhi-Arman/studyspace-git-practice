import { StrictMode } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import App from './App';

const valid = { status: 'ok', service: 'StudySpace', version: '0.1.0' };
const response = () => new Response(JSON.stringify(valid));

describe('initialization page', () => {
  it('shows the real connection result and labels all business functions as unimplemented', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response()));
    render(<App />);
    expect(await screen.findByText('连接成功')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Web教室与自习室预约管理系统');
    expect(screen.getByText(/注册、登录、查询、预约与管理功能均尚未实现/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /打开 API 文档/ })).toHaveAttribute('href', '/api/v1/docs');
    expect(screen.queryByRole('button', { name: '登录' })).not.toBeInTheDocument();
  });

  it('shows an invalid contract as failure and retries on user action', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ status: 'ok' })))
      .mockResolvedValueOnce(response());
    vi.stubGlobal('fetch', fetchMock);
    render(<App />);
    expect(await screen.findByText('连接失败')).toBeInTheDocument();
    expect(screen.getByText(/后端响应不符合健康接口合同/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: '重新检查' }));
    expect(await screen.findByText('连接成功')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('switches between Chinese, Russian and English without sending another health request', async () => {
    const fetchMock = vi.fn().mockResolvedValue(response());
    vi.stubGlobal('fetch', fetchMock);
    render(<App />);
    await screen.findByText('连接成功');
    await userEvent.click(screen.getByRole('button', { name: 'Русский' }));
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Система бронирования учебных аудиторий и мест для самостоятельной работы');
    expect(screen.getByText('Соединение установлено')).toBeInTheDocument();
    expect(document.documentElement.lang).toBe('ru-RU');
    await userEvent.click(screen.getByRole('button', { name: 'English' }));
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Web Classroom and Study Room Reservation System');
    expect(screen.getByText('Connected')).toBeInTheDocument();
    expect(document.documentElement.lang).toBe('en-US');
    expect(screen.getByRole('button', { name: 'English' })).toHaveAttribute('aria-pressed', 'true');
    expect(fetchMock).toHaveBeenCalledTimes(1);
    await userEvent.click(screen.getByRole('button', { name: '中文' }));
    expect(document.documentElement.lang).toBe('zh-CN');
  });

  it.each([
    {
      button: '中文',
      seat: /MVP面向教室与自习室内的单个座位/,
      identity: '注册、校内身份验证及登录',
      limits: /每次一个座位；同一学生预约时段不得重叠，非重叠时段可有多条预约；单次最长24小时/,
      obsoleteLimit: /当前未结束预约最多1条/,
      unavailable: /注册、登录、查询、预约与管理功能均尚未实现/,
      future: /^后续扩展：提醒、二维码签到、违约记录与资源使用率统计/,
      versions: /应用 0.1.0 · 文档 0.3.0/,
    },
    {
      button: 'Русский',
      seat: /MVP предусматривает бронирование отдельного места/,
      identity: 'Регистрация, проверка принадлежности к вузу и вход',
      limits: /Одно место на бронирование; интервалы одного студента не пересекаются, несколько непересекающихся бронирований разрешены; длительность не более 24 часов/,
      obsoleteLimit: /не более 1 текущего незавершённого бронирования/,
      unavailable: /Регистрация, вход, поиск, бронирование и администрирование пока не реализованы/,
      future: /^Дальнейшее расширение: напоминания, регистрация по QR-коду, учёт нарушений и статистика использования ресурсов/,
      versions: /Приложение 0.1.0 · Документы 0.3.0/,
    },
    {
      button: 'English',
      seat: /The MVP covers individual seats in classrooms and study rooms/,
      identity: 'Registration, university identity verification and sign-in',
      limits: /One seat per booking; a student's booking intervals must not overlap; multiple non-overlapping bookings are allowed; maximum duration of 24 hours/,
      obsoleteLimit: /at most 1 current unfinished booking/,
      unavailable: /Registration, sign-in, search, booking and administration are not implemented yet/,
      future: /^Future extensions: reminders, QR-code check-in, violation records and resource utilization statistics/,
      versions: /Application 0.1.0 · Documents 0.3.0/,
    },
  ])('presents the clarified seat scope and honest implementation status in $button', async (copy) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response()));
    render(<App />);
    await screen.findByText('连接成功');
    await userEvent.click(screen.getByRole('button', { name: copy.button }));
    expect(screen.getByText(copy.seat)).toBeInTheDocument();
    expect(screen.getByText(copy.identity)).toBeInTheDocument();
    expect(screen.getByText(copy.limits)).toBeInTheDocument();
    expect(screen.queryByText(copy.obsoleteLimit)).not.toBeInTheDocument();
    expect(screen.getByText(copy.unavailable)).toBeInTheDocument();
    expect(screen.getByText(copy.future)).toBeInTheDocument();
    expect(screen.getByText(copy.versions)).toBeInTheDocument();
  });

  it('cancels the first StrictMode request and keeps the active result', async () => {
    const signals: AbortSignal[] = [];
    const fetchMock = vi.fn((_url, init: RequestInit) => {
      const signal = init.signal as AbortSignal;
      signals.push(signal);
      if (signals.length > 1) return Promise.resolve(response());
      return new Promise((_resolve, reject) => signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError'))));
    });
    vi.stubGlobal('fetch', fetchMock);
    render(<StrictMode><App /></StrictMode>);
    expect(await screen.findByText('连接成功')).toBeInTheDocument();
    await waitFor(() => expect(signals[0].aborted).toBe(true));
    expect(signals[1].aborted).toBe(false);
  });
});
