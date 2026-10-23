import type { HealthErrorCode } from './api/health';

export type Language = 'zh-CN' | 'ru-RU' | 'en-US';

type Copy = {
  projectType: string;
  draft: string;
  title: string;
  introduction: string;
  scopeNotice: string;
  foundationLabel: string;
  foundationTitle: string;
  foundationDescription: string;
  connection: string;
  checking: string;
  connected: string;
  failed: string;
  contract: string;
  retry: string;
  apiDocs: string;
  healthBoundary: string;
  error: Record<HealthErrorCode, string>;
  roadmapLabel: string;
  roadmapTitle: string;
  planned: string;
  student: string;
  administrator: string;
  studentItems: string[];
  adminItems: string[];
  extension: string;
  footer: string;
};

export const content: Record<Language, Copy> = {
  'zh-CN': {
    projectType: '大学软件工程课程项目',
    draft: '初始化 · 草稿',
    title: 'Web教室与自习室预约管理系统',
    introduction: '为大学生和学校管理人员规划的预约平台，MVP面向教室与自习室内的单个座位。',
    scopeNotice: '当前版本仅包含工程基础结构与健康检查。注册、登录、查询、预约与管理功能均尚未实现。',
    foundationLabel: '01 / 工程基础',
    foundationTitle: '从可验证的基础开始',
    foundationDescription: '独立的前后端、清晰的接口边界，以及可逐步完善的双语工程文档。',
    connection: '后端连接状态',
    checking: '正在检查连接…',
    connected: '连接成功',
    failed: '连接失败',
    contract: '健康接口合同匹配版本 0.4.0',
    retry: '重新检查',
    apiDocs: '打开 API 文档',
    healthBoundary: '此检查只验证 API 基础连接，不代表预约业务已完成或通过验收。',
    error: {
      network: '无法连接后端，请确认后端已在 8000 端口启动。',
      http: '后端返回错误状态，请检查后端运行日志。',
      invalid_response: '后端响应不符合健康接口合同，请核对服务与版本。',
      timeout: '连接检查超过 5 秒，请确认后端服务可访问。',
    },
    roadmapLabel: '02 / MVP 开发范围',
    roadmapTitle: '先让一次预约可靠发生',
    planned: 'MVP范围已澄清 · 待开发',
    student: '学生',
    administrator: '管理员',
    studentItems: ['注册、校内身份验证及登录', '查询教室、自习室、空闲座位与可预约时段', '每次一个座位；同一学生预约时段不得重叠，非重叠时段可有多条预约；单次最长24小时', '取消预约与查看个人记录'],
    adminItems: ['角色权限与用户信息维护', '教室、自习室与开放时间管理', '预约规则与冲突检测', '预约记录与基础统计'],
    extension: '后续扩展：提醒、二维码签到、违约记录与资源使用率统计。扩展范围需单独确认。',
    footer: '应用 0.4.0 · 文档 0.3.0 · MVP范围与预约限制已澄清，正式SRS仍为草稿',
  },
  'ru-RU': {
    projectType: 'Учебный проект по программной инженерии',
    draft: 'Инициализация · Черновик',
    title: 'Система бронирования учебных аудиторий и мест для самостоятельной работы',
    introduction: 'Планируемая платформа для студентов и сотрудников вуза. MVP предусматривает бронирование отдельного места в учебной аудитории или помещении для самостоятельной работы.',
    scopeNotice: 'Текущая версия содержит только основу проекта и проверку работоспособности. Регистрация, вход, поиск, бронирование и администрирование пока не реализованы.',
    foundationLabel: '01 / Основа проекта',
    foundationTitle: 'Начинаем с проверяемой основы',
    foundationDescription: 'Отдельные клиентская и серверная части, чёткие границы API и двуязычная документация, которую можно последовательно дополнять.',
    connection: 'Соединение с сервером',
    checking: 'Проверка соединения…',
    connected: 'Соединение установлено',
    failed: 'Ошибка соединения',
    contract: 'Ответ проверки соответствует контракту версии 0.4.0',
    retry: 'Проверить снова',
    apiDocs: 'Открыть документацию API',
    healthBoundary: 'Проверка подтверждает только базовое соединение с API. Она не подтверждает готовность или приёмку функций бронирования.',
    error: {
      network: 'Сервер недоступен. Убедитесь, что он запущен на порту 8000.',
      http: 'Сервер вернул ошибку. Проверьте журнал работы сервера.',
      invalid_response: 'Ответ не соответствует контракту проверки. Проверьте сервис и версию.',
      timeout: 'Проверка заняла более 5 секунд. Убедитесь, что сервер доступен.',
    },
    roadmapLabel: '02 / Объём разработки MVP',
    roadmapTitle: 'Сначала — надёжное бронирование',
    planned: 'Объём MVP уточнён · Предстоит разработка',
    student: 'Студент',
    administrator: 'Администратор',
    studentItems: ['Регистрация, проверка принадлежности к вузу и вход', 'Поиск аудиторий, помещений для самостоятельной работы, свободных мест и доступных интервалов', 'Одно место на бронирование; интервалы одного студента не пересекаются, несколько непересекающихся бронирований разрешены; длительность не более 24 часов', 'Отмена бронирования и просмотр личной истории'],
    adminItems: ['Ролевой доступ и управление данными пользователей', 'Управление помещениями и временем работы', 'Правила бронирования и выявление конфликтов', 'История бронирований и базовая статистика'],
    extension: 'Дальнейшее расширение: напоминания, регистрация по QR-коду, учёт нарушений и статистика использования ресурсов. Объём расширения требует отдельного подтверждения.',
    footer: 'Приложение 0.4.0 · Документы 0.3.0 · Объём MVP и ограничения бронирования уточнены; официальная SRS остаётся черновиком',
  },
  'en-US': {
    projectType: 'University software engineering course project',
    draft: 'Initialization · Draft',
    title: 'Web Classroom and Study Room Reservation System',
    introduction: 'A planned booking platform for university students and staff. The MVP covers individual seats in classrooms and study rooms.',
    scopeNotice: 'This version contains only the project foundation and a health check. Registration, sign-in, search, booking and administration are not implemented yet.',
    foundationLabel: '01 / Project foundation',
    foundationTitle: 'Start with a verifiable foundation',
    foundationDescription: 'Separate frontend and backend applications, clear API boundaries and bilingual engineering documentation that can be developed step by step.',
    connection: 'Backend connection',
    checking: 'Checking the connection…',
    connected: 'Connected',
    failed: 'Connection failed',
    contract: 'The health response matches the version 0.4.0 contract',
    retry: 'Check again',
    apiDocs: 'Open API documentation',
    healthBoundary: 'This check verifies only the basic API connection. It does not confirm completion or acceptance of booking features.',
    error: {
      network: 'The backend could not be reached. Make sure it is running on port 8000.',
      http: 'The backend returned an error status. Check its application logs.',
      invalid_response: 'The response does not match the health contract. Check the service and version.',
      timeout: 'The check exceeded 5 seconds. Make sure the backend is accessible.',
    },
    roadmapLabel: '02 / MVP development scope',
    roadmapTitle: 'Make each booking reliable',
    planned: 'MVP scope clarified · Development pending',
    student: 'Student',
    administrator: 'Administrator',
    studentItems: ['Registration, university identity verification and sign-in', 'Search classrooms, study rooms, available seats and booking intervals', "One seat per booking; a student's booking intervals must not overlap; multiple non-overlapping bookings are allowed; maximum duration of 24 hours", 'Cancel bookings and view personal booking history'],
    adminItems: ['Role-based access and user information maintenance', 'Classroom, study room and opening-hour management', 'Booking rules and conflict detection', 'Booking records and basic statistics'],
    extension: 'Future extensions: reminders, QR-code check-in, violation records and resource utilization statistics. Their scope requires separate confirmation.',
    footer: 'Application 0.4.0 · Documents 0.3.0 · MVP scope and booking limits clarified; the formal SRS remains a draft',
  },
};
