import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import App from "./App";

const student = {
  id: 1,
  username: "demo_student",
  display_name: "演示同学",
  role: "STUDENT",
  enabled: true,
  identity_mode: "LOCAL_ONLY",
};
const room = {
  id: 1,
  name: "演示空间 A",
  campus: "Demo",
  building: "Library",
  floor: 2,
  kind: "STUDY_ROOM",
  description: "Local demonstration",
  enabled: true,
  capacity: 2,
  seat_count: 2,
  opens_at: "08:00",
  closes_at: "22:00",
  regular_opens_at: "08:00",
  regular_closes_at: "22:00",
  closed: false,
};
const policy = {
  today: "2030-01-01",
  server_now: "2030-01-01T00:10:00Z",
  timezone: "Asia/Shanghai",
  advance_days: 7,
  granularity_minutes: 30,
  max_duration_hours: 24,
  identity_mode: "LOCAL_ONLY",
};
const reply = (data: unknown, status = 200) =>
  new Response(status === 204 ? null : JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });

function server({ signedIn = false, conflict = false } = {}) {
  let authenticated = signedIn;
  let booking: Record<string, unknown> | null = null;
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input), "http://localhost");
      const path = url.pathname;
      if (path.endsWith("/auth/me"))
        return authenticated
          ? reply(student)
          : reply({ error: { code: "AUTH_REQUIRED" } }, 401);
      if (path.endsWith("/policy")) return reply(policy);
      if (path.endsWith("/auth/register")) return reply(student, 201);
      if (path.endsWith("/auth/login")) {
        const body = JSON.parse(String(init?.body));
        if (body.password === "wrong-password")
          return reply({ error: { code: "INVALID_CREDENTIALS" } }, 401);
        authenticated = true;
        return reply(student);
      }
      if (path.endsWith("/auth/logout")) {
        authenticated = false;
        return reply(null, 204);
      }
      if (path.endsWith("/rooms"))
        return reply({ items: [room], total: 1, page: 1, page_size: 20 });
      if (path.endsWith("/seats"))
        return reply({
          room,
          items: [
            {
              id: 1,
              code: "A01",
              room_id: 1,
              enabled: true,
              available: !booking || booking.status === "CANCELLED",
            },
            { id: 2, code: "A02", room_id: 1, enabled: true, available: true },
          ],
        });
      if (path.endsWith("/cancel")) {
        if (booking)
          booking = {
            ...booking,
            status: "CANCELLED",
            can_cancel: false,
            cancelled_at: "2030-01-01T00:20:00Z",
            cancellation_reason: "STUDENT_CANCELLED",
          };
        return reply(booking);
      }
      if (path.endsWith("/bookings") && init?.method === "POST") {
        if (conflict) return reply({ error: { code: "USER_CONFLICT" } }, 409);
        const body = JSON.parse(String(init.body));
        booking = {
          id: 1,
          seat_id: body.seat_id,
          seat_code: body.seat_id === 1 ? "A01" : "A02",
          room_id: 1,
          room_name: room.name,
          business_date: body.starts_at.slice(0, 10),
          starts_at: body.starts_at,
          ends_at: body.ends_at,
          created_at: "2030-01-01T00:10:00Z",
          cancelled_at: null,
          cancellation_reason: null,
          status: "UPCOMING",
          can_cancel: true,
        };
        return reply(booking, 201);
      }
      if (path.endsWith("/bookings"))
        return reply({
          items: booking ? [booking] : [],
          total: booking ? 1 : 0,
          page: 1,
          page_size: 20,
          history_from: "2029-07-01",
        });
      return reply({ error: { code: "NOT_FOUND" } }, 404);
    }),
  );
}

async function login() {
  await userEvent.click(screen.getByRole("button", { name: "登录" }));
  const dialog = screen.getByRole("dialog");
  await userEvent.type(within(dialog).getByLabelText("用户名"), "demo_student");
  await userEvent.type(
    within(dialog).getByLabelText("密码"),
    "Local-demo-password42!",
  );
  await userEvent.click(within(dialog).getByRole("button", { name: "登录" }));
  await screen.findByText("演示同学");
}

describe("local reservation application", () => {
  it("shows real room availability and clearly labels the local identity mode", async () => {
    server();
    render(<App />);
    expect(await screen.findByRole("button", { name: /A01/ })).toBeEnabled();
    expect(screen.getByText(/无需真实学校身份验证/)).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "给专注，留一个位置",
    );
  });

  it("signs in, reserves a seat, and cancels the real visible personal record", async () => {
    server();
    render(<App />);
    await screen.findByRole("button", { name: /A01/ });
    await login();
    fireEvent.change(screen.getByLabelText("预约日期"), {
      target: { value: "2030-01-03" },
    });
    await screen.findByRole("button", { name: /A01/ });
    await userEvent.click(screen.getByRole("button", { name: /A01/ }));
    await userEvent.click(screen.getByRole("button", { name: "预约这个座位" }));
    await userEvent.click(
      within(screen.getByRole("dialog")).getByRole("button", {
        name: "确认预约",
      }),
    );
    await screen.findByText(/预约成功，座位已为你留好。/);
    expect(screen.getByLabelText("预约日期")).toHaveValue("2030-01-03");
    await userEvent.click(screen.getByRole("button", { name: "我的预约" }));
    expect(await screen.findByText("A01")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "取消预约" }));
    await userEvent.click(
      within(screen.getByRole("dialog")).getByRole("button", {
        name: "确认取消",
      }),
    );
    expect(
      await within(await screen.findByRole("article")).findByText("已取消"),
    ).toBeInTheDocument();
  });

  it("keeps a conflict visible without showing a success or a fabricated booking", async () => {
    server({ signedIn: true, conflict: true });
    render(<App />);
    await screen.findByText("演示同学");
    await userEvent.click(await screen.findByRole("button", { name: /A01/ }));
    await userEvent.click(screen.getByRole("button", { name: "预约这个座位" }));
    await userEvent.click(
      within(screen.getByRole("dialog")).getByRole("button", {
        name: "确认预约",
      }),
    );
    expect(await screen.findByText(/你在这个时段已有预约/)).toBeInTheDocument();
    expect(
      screen.queryByText("预约成功，座位已为你留好。"),
    ).not.toBeInTheDocument();
  });

  it("switches booking labels between all three languages", async () => {
    server();
    render(<App />);
    await screen.findByRole("button", { name: /A01/ });
    await userEvent.click(screen.getByRole("button", { name: "Русский" }));
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Место для сосредоточенной работы",
    );
    expect(document.documentElement.lang).toBe("ru-RU");
    await userEvent.click(screen.getByRole("button", { name: "English" }));
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Make room for focus",
    );
    expect(screen.getByLabelText("Booking date")).toBeInTheDocument();
    expect(document.documentElement.lang).toBe("en-US");
  });

  it("registers a local account and reports incorrect credentials inside the form", async () => {
    server();
    render(<App />);
    await screen.findByRole("button", { name: /A01/ });
    await userEvent.click(screen.getByRole("button", { name: "登录" }));
    let dialog = screen.getByRole("dialog");
    await userEvent.type(
      within(dialog).getByLabelText("用户名"),
      "demo_student",
    );
    await userEvent.type(
      within(dialog).getByLabelText("密码"),
      "wrong-password",
    );
    await userEvent.click(within(dialog).getByRole("button", { name: "登录" }));
    expect(await screen.findByText("用户名或密码不正确。")).toBeInTheDocument();
    await userEvent.click(
      within(dialog).getByRole("button", { name: "注册账号" }),
    );
    dialog = screen.getByRole("dialog");
    await userEvent.type(within(dialog).getByLabelText("显示名称"), "演示同学");
    fireEvent.change(within(dialog).getByLabelText("密码"), {
      target: { value: "Local-demo-password42!" },
    });
    await userEvent.click(
      within(dialog).getByRole("button", { name: "创建本地账号" }),
    );
    expect(await screen.findByText("演示同学")).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("does not let a delayed anonymous session probe undo a successful sign in", async () => {
    server();
    const original = vi.mocked(fetch).getMockImplementation()!;
    let resolveProbe!: (response: Response) => void;
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
        if (String(input).endsWith("/auth/me"))
          return new Promise<Response>((resolve) => {
            resolveProbe = resolve;
          });
        return original(input, init);
      }),
    );
    render(<App />);
    await screen.findByRole("button", { name: /A01/ });
    await login();
    await act(async () => {
      resolveProbe(reply({ error: { code: "AUTH_REQUIRED" } }, 401));
    });
    await waitFor(() =>
      expect(screen.getByText("演示同学")).toBeInTheDocument(),
    );
  });

  it("keeps the latest availability result when an older request finishes late", async () => {
    server();
    const original = vi.mocked(fetch).getMockImplementation()!;
    let resolveOld!: (response: Response) => void;
    let requested = false;
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
        if (String(input).includes("/seats?")) {
          if (!requested) {
            requested = true;
            return new Promise<Response>((resolve) => {
              resolveOld = resolve;
            });
          }
          return Promise.resolve(
            reply({
              room,
              items: [
                {
                  id: 2,
                  code: "A02",
                  room_id: 1,
                  enabled: true,
                  available: true,
                },
              ],
            }),
          );
        }
        return original(input, init);
      }),
    );
    render(<App />);
    await waitFor(() => expect(requested).toBe(true));
    fireEvent.change(screen.getByLabelText("预约日期"), {
      target: { value: "2030-01-02" },
    });
    await screen.findByRole("button", { name: /A02/ });
    await act(async () => {
      resolveOld(
        reply({
          room,
          items: [
            { id: 1, code: "A01", room_id: 1, enabled: true, available: true },
          ],
        }),
      );
    });
    expect(screen.getByRole("button", { name: /A02/ })).toBeEnabled();
    expect(
      screen.queryByRole("button", { name: /A01/ }),
    ).not.toBeInTheDocument();
  });
  it("serializes a 24:00 end as next-day midnight for queries and booking", async () => {
    server({ signedIn: true });
    render(<App />);
    await screen.findByText("演示同学");
    fireEvent.change(screen.getByLabelText("预约日期"), {
      target: { value: "2030-01-02" },
    });
    await userEvent.selectOptions(screen.getByLabelText("开始时间"), "00:00");
    await userEvent.selectOptions(screen.getByLabelText("结束时间"), "24:00");
    await userEvent.click(await screen.findByRole("button", { name: /A01/ }));
    await userEvent.click(screen.getByRole("button", { name: "预约这个座位" }));
    expect(
      within(screen.getByRole("dialog")).getByText("00:00–24:00"),
    ).toBeInTheDocument();
    await userEvent.click(
      within(screen.getByRole("dialog")).getByRole("button", {
        name: "确认预约",
      }),
    );
    await screen.findByText("预约成功，座位已为你留好。");
    const post = vi
      .mocked(fetch)
      .mock.calls.find(
        ([path, init]) =>
          String(path).endsWith("/bookings") && init?.method === "POST",
      )!;
    expect(JSON.parse(String(post[1]?.body)).ends_at).toBe(
      "2030-01-03T00:00:00+08:00",
    );
    const latestQuery = vi
      .mocked(fetch)
      .mock.calls.filter(([path]) => String(path).includes("/seats?"))
      .at(-1)!;
    expect(
      new URL(String(latestQuery[0]), "http://localhost").searchParams.get(
        "ends_at",
      ),
    ).toBe("2030-01-03T00:00:00+08:00");
  });

  it.each(["21:01", "22:01"])(
    "allows available late half-hour slots at %s with a one-day window",
    async (clock) => {
      server({ signedIn: true });
      const original = vi.mocked(fetch).getMockImplementation()!;
      vi.stubGlobal(
        "fetch",
        vi.fn((path: RequestInfo | URL, init?: RequestInit) =>
          String(path).endsWith("/policy")
            ? Promise.resolve(
                reply({
                  ...policy,
                  advance_days: 1,
                  server_now: `2030-01-01T${clock}:00+08:00`,
                }),
              )
            : original(path, init),
        ),
      );
      render(<App />);
      await screen.findByText("演示同学");
      const hour = Number(clock.slice(0, 2));
      await userEvent.selectOptions(
        screen.getByLabelText("开始时间"),
        `${hour}:30`,
      );
      await userEvent.selectOptions(
        screen.getByLabelText("结束时间"),
        `${hour + 1}:00`,
      );
      const seat = await screen.findByRole("button", { name: /A01/ });
      expect(seat).toBeEnabled();
      await userEvent.click(seat);
      expect(
        screen.getByRole("button", { name: "预约这个座位" }),
      ).toBeEnabled();
    },
  );

  it("retries a failed admin read without claiming a successful save", async () => {
    server({ signedIn: true });
    const original = vi.mocked(fetch).getMockImplementation()!;
    vi.stubGlobal(
      "fetch",
      vi.fn((path: RequestInfo | URL, init?: RequestInit) => {
        if (String(path).endsWith("/auth/me"))
          return Promise.resolve(reply({ ...student, role: "ADMIN" }));
        if (String(path).endsWith("/admin/rooms"))
          return Promise.resolve(
            reply({ error: { code: "REQUEST_FAILED" } }, 503),
          );
        return original(path, init);
      }),
    );
    render(<App />);
    await userEvent.click(
      await screen.findByRole("button", { name: "管理工作台" }),
    );
    await userEvent.click(await screen.findByRole("button", { name: "重试" }));
    await screen.findByRole("button", { name: "重试" });
    expect(screen.queryByText("已保存。")).not.toBeInTheDocument();
  });
});
