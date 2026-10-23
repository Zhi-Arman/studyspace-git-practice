export type Language = "zh-CN" | "ru-RU" | "en-US";
const words = {
  capacity: ["座位数", "Мест", "Seats"],
  planEyebrow: ["你的专注安排", "ВАШ УЧЕБНЫЙ ПЛАН", "YOUR STUDY PLAN"],
  adminEyebrow: ["空间维护", "УПРАВЛЕНИЕ ПРОСТРАНСТВОМ", "SPACE KEEPING"],
  registerAction: ["创建账号", "Регистрация аккаунта", "Account created"],
  loginAction: ["登录", "Вход", "Signed in"],
  createRoomAction: ["创建空间", "Создание помещения", "Space created"],
  updateRoomAction: ["更新空间", "Изменение помещения", "Space updated"],
  createSeatAction: ["创建座位", "Создание места", "Seat created"],
  updateSeatAction: ["更新座位", "Изменение места", "Seat updated"],
  exceptionAction: [
    "调整日期例外",
    "Исключение по дате",
    "Date exception changed",
  ],
  policyAction: [
    "调整预约窗口",
    "Изменение окна бронирования",
    "Booking window changed",
  ],
  userAction: ["更新账号权限", "Изменение прав", "Account access updated"],
  seedAction: [
    "初始化演示空间",
    "Создание деморесурсов",
    "Demo spaces initialized",
  ],
  adminAction: [
    "创建管理员",
    "Создание администратора",
    "Administrator created",
  ],

  find: ["找个座位", "Найти место", "Find a seat"],
  mine: ["我的预约", "Мои бронирования", "My bookings"],
  admin: ["管理工作台", "Управление", "Administration"],
  local: ["本地课程版", "Локальная учебная версия", "Local course edition"],
  privacy: [
    "仅供本地演示，无需真实学校身份验证。",
    "Локальная демонстрация без реальной проверки принадлежности к вузу.",
    "Local demonstration. No real university identity verification.",
  ],
  headline: [
    "给专注，留一个位置。",
    "Место для сосредоточенной работы",
    "Make room for focus.",
  ],
  intro: [
    "选一个安静的角落，安排下一段专注时光。",
    "Выберите тихий уголок для следующего часа учёбы.",
    "A quiet corner for your next good hour of work.",
  ],
  eyebrow: ["YOUR NEXT QUIET HOUR", "ВАШ ТИХИЙ ЧАС", "YOUR NEXT QUIET HOUR"],
  login: ["登录", "Войти", "Sign in"],
  logout: ["退出", "Выйти", "Sign out"],
  register: ["注册账号", "Регистрация", "Create account"],
  createAccount: [
    "创建本地账号",
    "Создать локальный аккаунт",
    "Create local account",
  ],
  username: ["用户名", "Логин", "Username"],
  password: ["密码", "Пароль", "Password"],
  displayName: ["显示名称", "Отображаемое имя", "Display name"],
  accountHint: [
    "用户名为3–32位字母、数字或下划线；密码至少10位。请使用演示信息。",
    "Логин: 3–32 латинские буквы, цифры или _. Пароль: от 10 символов. Используйте учебные данные.",
    "Username: 3–32 letters, digits or _. Password: at least 10 characters. Use demonstration details.",
  ],
  close: ["关闭", "Закрыть", "Close"],
  back: ["返回", "Назад", "Back"],
  busy: ["处理中…", "Обработка…", "Working…"],
  loading: ["正在载入…", "Загрузка…", "Loading…"],
  retry: ["重试", "Повторить", "Try again"],
  bookingDate: ["预约日期", "Дата бронирования", "Booking date"],
  start: ["开始时间", "Начало", "Start time"],
  end: ["结束时间", "Окончание", "End time"],
  search: ["查询座位", "Найти места", "Search seats"],
  campus: ["校区", "Кампус", "Campus"],
  building: ["楼栋", "Здание", "Building"],
  floor: ["楼层", "Этаж", "Floor"],
  kind: ["空间类型", "Тип помещения", "Space type"],
  all: ["全部", "Все", "All"],
  classroom: ["教室", "Аудитория", "Classroom"],
  studyRoom: ["自习室", "Читальный зал", "Study room"],
  spaces: ["选择空间", "Выберите помещение", "Choose a space"],
  spacesHint: [
    "演示空间，开放时间以当天配置为准。",
    "Учебные помещения; расписание зависит от даты.",
    "Demonstration spaces. Hours may vary by date.",
  ],
  seats: ["选择座位", "Выберите место", "Choose a seat"],
  seat: ["座位", "Место", "Seat"],
  available: ["可预约", "Свободно", "Available"],
  unavailable: ["不可预约", "Недоступно", "Unavailable"],
  selected: ["已选择", "Выбрано", "Selected"],
  disabled: ["已停用", "Отключено", "Disabled"],
  enabled: ["启用", "Включено", "Enabled"],
  opening: ["开放时间", "Часы работы", "Opening hours"],
  closed: ["当天关闭", "Закрыто в этот день", "Closed on this date"],
  emptyRooms: [
    "没有符合条件的空间，请调整筛选。",
    "Подходящих помещений нет. Измените фильтры.",
    "No matching spaces. Try different filters.",
  ],
  emptySeats: [
    "这个空间还没有座位，请选择其他空间。",
    "В этом помещении пока нет мест. Выберите другое.",
    "No seats have been added here yet. Choose another space.",
  ],
  outsideHours: [
    "所选时段不在开放窗口内，或座位已被预约。",
    "Интервал вне расписания или места уже заняты.",
    "This interval is outside opening hours, or the seats are already booked.",
  ],
  chooseSeat: [
    "从座位图中选择一个可预约座位。",
    "Выберите свободное место на схеме.",
    "Choose an available seat from the grid.",
  ],
  reserve: ["预约这个座位", "Забронировать место", "Reserve this seat"],
  loginToBook: ["登录后预约", "Войдите для бронирования", "Sign in to reserve"],
  confirmBooking: ["确认预约", "Подтвердить", "Confirm booking"],
  reviewBooking: [
    "确认这段专注时光",
    "Подтвердите время",
    "Your next focused hour",
  ],
  bookingSuccess: [
    "预约成功，座位已为你留好。",
    "Готово. Место забронировано.",
    "Booked. Your seat is ready for you.",
  ],
  ruleHint: [
    "一次一个座位；同一用户的预约时段不能重叠。相邻或不重叠的预约可以有多条。",
    "Одно место за раз. Интервалы пользователя не пересекаются; соседние и непересекающиеся разрешены.",
    "One seat per booking. Your bookings cannot overlap; adjacent and separate intervals are welcome.",
  ],
  timezone: [
    "所有时间均为上海时间（UTC+8）",
    "Время Шанхая (UTC+8)",
    "All times are Shanghai time (UTC+8)",
  ],
  noSlots: [
    "今天已没有可预约时段，请选择其他日期。",
    "На сегодня доступных интервалов нет. Выберите другую дату.",
    "No bookable intervals remain today. Choose another date.",
  ],
  studentOnly: [
    "请使用学生账号预约座位。",
    "Для бронирования нужен аккаунт студента.",
    "Use a student account to reserve seats.",
  ],
  mineIntro: [
    "你的安排，清楚地放在这里。开始前可以自行取消。",
    "Все планы здесь. До начала запись можно отменить.",
    "Your plans, in one place. You can cancel before a booking starts.",
  ],
  noBookings: [
    "还没有预约。去选一个喜欢的座位吧。",
    "Бронирований пока нет. Выберите место.",
    "No bookings yet. Find a seat you like.",
  ],
  status: ["状态", "Статус", "Status"],
  UPCOMING: ["未开始", "Предстоит", "Upcoming"],
  ONGOING: ["进行中", "Сейчас", "In progress"],
  COMPLETED: ["已结束", "Завершено", "Completed"],
  CANCELLED: ["已取消", "Отменено", "Cancelled"],
  cancelBooking: ["取消预约", "Отменить бронь", "Cancel booking"],
  confirmCancel: ["确认取消", "Подтвердить отмену", "Confirm cancellation"],
  cancelHint: [
    "取消后，这个时段的座位会重新开放。其他预约不受影响。",
    "Место снова станет доступно. Остальные записи сохранятся.",
    "The seat will become available for this interval. Your other bookings stay in place.",
  ],
  cancelled: ["预约已取消。", "Бронирование отменено.", "Booking cancelled."],
  previous: ["上一页", "Назад", "Previous"],
  next: ["下一页", "Далее", "Next"],
  page: ["页", "Страница", "Page"],
  reason: ["操作原因", "Причина", "Reason"],
  cancelReason: ["取消原因", "Причина отмены", "Cancellation reason"],
  save: ["保存", "Сохранить", "Save"],
  saved: ["已保存。", "Сохранено.", "Saved."],
  edit: ["编辑", "Изменить", "Edit"],
  add: ["新增", "Добавить", "Add"],
  adminIntro: [
    "维护空间、开放时间和账号，查看预约记录。",
    "Ресурсы, расписание, аккаунты и бронирования.",
    "Manage spaces, hours, accounts and bookings.",
  ],
  resources: ["资源与开放", "Ресурсы и расписание", "Spaces & hours"],
  records: ["预约与统计", "Записи и статистика", "Bookings & totals"],
  users: ["用户与权限", "Пользователи и права", "Users & access"],
  audit: ["操作记录", "Журнал действий", "Activity log"],
  roomName: ["空间名称", "Название", "Space name"],
  description: ["说明", "Описание", "Description"],
  newRoom: ["新增空间", "Добавить помещение", "Add space"],
  editRoom: ["编辑空间", "Изменить помещение", "Edit space"],
  seatCode: ["座位编号", "Код места", "Seat code"],
  newSeat: ["新增座位", "Добавить место", "Add seat"],
  editSeat: ["编辑座位", "Изменить место", "Edit seat"],
  dateExceptions: ["日期例外", "Исключения по датам", "Date exceptions"],
  dateExceptionHint: [
    "日期例外优先于常规开放时间；关闭或缩短时段会取消受影响的预约。",
    "Исключения важнее обычного расписания. Закрытие или сужение отменяет затронутые записи.",
    "Date exceptions override regular hours. Closing or narrowing hours cancels affected bookings.",
  ],
  remove: ["移除", "Удалить", "Remove"],
  confirmChange: ["确认变更", "Подтвердить изменение", "Confirm change"],
  changeHint: [
    "停用或缩短开放时间，会自动取消受影响的未结束预约。重新启用不会恢复已取消预约。",
    "Отключение или сужение расписания отменяет затронутые записи. Включение их не восстанавливает.",
    "Disabling or narrowing hours cancels affected unfinished bookings. Re-enabling does not restore them.",
  ],
  policy: ["预约窗口", "Окно бронирования", "Booking window"],
  days: ["个自然日", "календарных дней", "calendar days"],
  advanceDays: [
    "可提前预约天数",
    "Глубина бронирования",
    "Advance booking days",
  ],
  created: ["累计创建", "Всего создано", "Created"],
  cancelledCount: ["累计取消", "Отменено", "Cancelled"],
  active: ["尚未结束", "Ещё не завершены", "Unfinished"],
  snapshot: ["统计截至", "Срез на", "Snapshot at"],
  statsHint: [
    "按预约日期统计，不代表实际到场或使用率。",
    "По дате бронирования, не по посещаемости или загрузке.",
    "By booking date. These totals do not measure attendance or utilization.",
  ],
  role: ["角色", "Роль", "Role"],
  STUDENT: ["学生", "Студент", "Student"],
  ADMIN: ["管理员", "Администратор", "Administrator"],
  userHint: [
    "停用会立即撤销会话并取消未结束预约；至少保留一位启用的管理员。",
    "Отключение отзывает сессии и отменяет незавершённые записи. Один активный администратор должен остаться.",
    "Disabling revokes sessions and cancels unfinished bookings. One enabled administrator must remain.",
  ],
  noUsers: [
    "没有符合条件的账号。",
    "Подходящих аккаунтов нет.",
    "No matching accounts.",
  ],
  action: ["动作", "Действие", "Action"],
  target: ["目标", "Объект", "Target"],
  time: ["时间", "Время", "Time"],
  actor: ["操作者编号", "ID участника", "Actor ID"],
  retained: [
    "历史按180天保留策略展示。",
    "История хранится 180 дней.",
    "History follows the 180-day retention policy.",
  ],
  requestFailed: [
    "请求未完成，请重试。",
    "Запрос не выполнен. Повторите.",
    "The request did not finish. Please try again.",
  ],
  network: [
    "无法连接本地服务，请确认应用已启动。",
    "Локальный сервис недоступен. Проверьте запуск.",
    "Cannot reach the local service. Check that the application is running.",
  ],
  timeout: [
    "请求超时，请稍后重试。",
    "Время ожидания истекло. Повторите позже.",
    "The request timed out. Please try again.",
  ],
  validation: [
    "请检查填写内容和时间范围。",
    "Проверьте поля и временной интервал.",
    "Check the form fields and time range.",
  ],
  badLogin: [
    "用户名或密码不正确。",
    "Неверный логин или пароль.",
    "Username or password is incorrect.",
  ],
  taken: [
    "这个用户名已被使用，请换一个。",
    "Этот логин уже занят.",
    "This username is already in use.",
  ],
  authRequired: [
    "登录已失效，请重新登录。",
    "Сессия истекла. Войдите снова.",
    "Your session ended. Please sign in again.",
  ],
  userConflict: [
    "你在这个时段已有预约，请选择不重叠的时间。",
    "У вас уже есть запись на этот интервал. Выберите другое время.",
    "You already have a booking during this interval. Choose another time.",
  ],
  seatConflict: [
    "这个座位刚刚被预约，请重新选择。",
    "Место только что заняли. Выберите другое.",
    "This seat was just booked. Choose another seat.",
  ],
  outside: [
    "所选时段不在开放时间内。",
    "Интервал вне часов работы.",
    "This interval is outside opening hours.",
  ],
  past: [
    "预约开始时间必须晚于现在。",
    "Начало должно быть в будущем.",
    "The booking must start in the future.",
  ],
  window: [
    "请选择预约窗口内的日期。",
    "Выберите дату в доступном окне.",
    "Choose a date inside the booking window.",
  ],
  tooLate: [
    "预约已经开始或结束，请联系管理员处理。",
    "Запись уже началась или завершена. Обратитесь к администратору.",
    "This booking has started or finished. Contact an administrator.",
  ],
  lastAdmin: [
    "至少需要保留一位启用的管理员。",
    "Нужен хотя бы один активный администратор.",
    "At least one enabled administrator must remain.",
  ],
  reasonRequired: [
    "请填写操作原因。",
    "Укажите причину.",
    "Please provide a reason.",
  ],
  historyExpired: [
    "该日期已超出保留期，无法提供完整统计。",
    "Дата вне срока хранения; полная статистика недоступна.",
    "This date is outside retention. Complete history is unavailable.",
  ],
  throttled: [
    "尝试次数过多，请5分钟后重试。",
    "Слишком много попыток. Подождите 5 минут.",
    "Too many attempts. Try again in five minutes.",
  ],
  resourceDisabled: [
    "这个资源已停用，请重新选择。",
    "Ресурс отключён. Выберите другой.",
    "This resource is disabled. Choose another.",
  ],
  codeTaken: [
    "该空间内已有相同座位编号。",
    "Такой код места уже есть в помещении.",
    "This seat code already exists in the space.",
  ],
  clear: ["清除筛选", "Сбросить фильтры", "Clear filters"],
  signInHint: [
    "登录后查看自己的预约。",
    "Войдите, чтобы увидеть свои записи.",
    "Sign in to see your bookings.",
  ],
} as const;
export type Message = keyof typeof words;
export type T = (key: Message) => string;
export function translator(language: Language): T {
  const index = language === "zh-CN" ? 0 : language === "ru-RU" ? 1 : 2;
  return (key) => words[key][index];
}
export function errorText(error: unknown, t: T) {
  const code =
    typeof error === "object" && error !== null && "code" in error
      ? String(error.code)
      : "";
  const keys: Record<string, Message> = {
    NETWORK: "network",
    TIMEOUT: "timeout",
    VALIDATION_ERROR: "validation",
    INVALID_CREDENTIALS: "badLogin",
    USERNAME_TAKEN: "taken",
    AUTH_REQUIRED: "authRequired",
    USER_CONFLICT: "userConflict",
    SEAT_CONFLICT: "seatConflict",
    OUTSIDE_OPENING: "outside",
    TIME_BOUNDARY: "validation",
    TIME_RANGE: "validation",
    START_IN_PAST: "past",
    BOOKING_WINDOW: "window",
    CANCEL_TOO_LATE: "tooLate",
    BOOKING_COMPLETED: "tooLate",
    LAST_ADMIN: "lastAdmin",
    REASON_REQUIRED: "reasonRequired",
    HISTORY_EXPIRED: "historyExpired",
    LOGIN_THROTTLED: "throttled",
    RESOURCE_DISABLED: "resourceDisabled",
    SEAT_CODE_TAKEN: "codeTaken",
    ADMIN_REQUIRED: "authRequired",
    STUDENT_REQUIRED: "studentOnly",
  };
  return t(keys[code] || "requestFailed");
}
export function formatTime(
  value: string | null,
  language: Language,
  withDate = false,
) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(language, {
    timeZone: "Asia/Shanghai",
    ...(withDate ? ({ month: "2-digit", day: "2-digit" } as const) : {}),
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).format(new Date(value));
}
export function addDays(day: string, days: number) {
  const d = new Date(`${day}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

export function actionText(action: string, t: T) {
  const mapping: Record<string, Message> = {
    REGISTER: "registerAction",
    LOGIN: "loginAction",
    CREATE_ROOM: "createRoomAction",
    UPDATE_ROOM: "updateRoomAction",
    CREATE_SEAT: "createSeatAction",
    UPDATE_SEAT: "updateSeatAction",
    SET_OPENING_EXCEPTION: "exceptionAction",
    REMOVE_OPENING_EXCEPTION: "exceptionAction",
    UPDATE_POLICY: "policyAction",
    UPDATE_USER: "userAction",
    SEED_DEMO: "seedAction",
    CREATE_ADMIN_CLI: "adminAction",
    CREATE_BOOKING: "confirmBooking",
    CANCEL_BOOKING: "cancelBooking",
  };
  return t(mapping[action] || "action");
}
