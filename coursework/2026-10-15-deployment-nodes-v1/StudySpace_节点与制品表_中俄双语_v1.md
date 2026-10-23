# StudySpace 节点与制品表

# StudySpace Узлы и артефакты

SS-DEP-T1-01 · v1 · 2026-10-15 · DRAFT



StudySpace 采用 React 浏览器客户端与 FastAPI 模块化单体；开发使用 SQLite，目标部署选择 Docker Compose、Caddy 和 PostgreSQL。下表按课堂五个字段列出节点、制品与通信方式，并保留现有配置和目标方案的状态。

StudySpace использует браузерный клиент React и модульный монолит FastAPI; для разработки — SQLite, для целевого размещения выбраны Docker Compose, Caddy и PostgreSQL. Таблица содержит пять полей задания и сохраняет статусы текущих конфигураций и целевой схемы.



| 节点<br>Узел | 类型<br>Тип | 部署的组件与制品<br>Размещаемые компоненты / артефакты | 端口与协议<br>Порты и протоколы | 环境<br>Среда |

| --- | --- | --- | --- | --- |

| N-01<br>学生或管理员终端<br>Устройство студента или администратора | 设备<br>电脑或手机<br>Устройство<br>ПК или телефон | 浏览器执行 CMP-001 界面代码；从前端服务下载 HTML、JavaScript 和 CSS。<br>Браузер исполняет интерфейс CMP-001 и получает HTML, JavaScript и CSS от сервиса клиента. | 无固定入站服务端口。开发访问 HTTP 5173；本地容器访问 HTTP 8080；目标 HTTPS 443。<br>Постоянный входящий порт не нужен. HTTP 5173 при разработке, HTTP 8080 для локальных контейнеров, целевой HTTPS 443. | 开发及目标使用端<br>目标 HTTPS 待部署<br>Клиент разработки и целевой среды<br>HTTPS ещё не развёрнут |

| N-02<br>本地开发工作站<br>Локальная рабочая станция | 设备<br>本地服务宿主<br>Устройство<br>Хост локальных сервисов | Vite 提供 CMP-001；Uvicorn 运行<br>FastAPI 与 SQLAlchemy 基础层。SQLite 文件 backend/data/studyspace.db 随后端访问；业务模块待实现。<br>Vite обслуживает CMP-001; Uvicorn запускает FastAPI и основу SQLAlchemy. Сервер обращается к файлу backend/data/studyspace.db SQLite; бизнес-модули ещё не реализованы. | 127.0.0.1:5173 HTTP；/api 代理至 127.0.0.1:8000，HTTP/JSON。SQLite 使用文件访问，无网络端口。<br>127.0.0.1:5173 HTTP; /api передаётся на 127.0.0.1:8000 по HTTP/JSON. SQLite использует файл без сетевого порта. | development<br>现有启动配置<br>development<br>Имеющаяся конфигурация запуска |

| N-03<br>前端静态服务<br>Сервис статического клиента | 容器<br>Nginx<br>Контейнер<br>Nginx | CMP-001 的分发制品：frontend/dist 中的 index.html 与 assets；镜像内位于 /usr/share/nginx/html。nginx.conf 配置静态服务和 /api/ 转发。<br>Артефакты CMP-001: index.html и assets из frontend/dist, в образе — /usr/share/nginx/html. nginx.conf задаёт статику и прокси /api/. | 127.0.0.1:8080 → 80，HTTP。<br>/api/ → backend:8000，<br>HTTP/JSON。<br>目标由 Caddy 提供 HTTPS。<br>Локально 127.0.0.1:8080 → порт 80 контейнера, HTTP. /api/ → backend:8000, HTTP/JSON. В целевой схеме HTTPS предоставляет Caddy. | 本地容器候选<br>配置已存在<br>目标部署待实施<br>Локальный вариант контейнеров<br>Конфигурация есть<br>Целевое размещение впереди |

| N-04<br>后端应用服务<br>Сервис приложения | 容器<br>Python<br>Uvicorn<br>Контейнер<br>Python<br>Uvicorn | backend/app 与依赖环境；FastAPI、Pydantic、同步 SQLAlchemy。CMP-002 至 CMP-008 为设计中的认证、审核、资源、查询、预约、统计及审计模块；CMP-009 的数据访问基础层已存在。<br>backend/app и зависимости; FastAPI, Pydantic, синхронный SQLAlchemy. CMP-002–CMP-008 проектируют аутентификацию, проверку, ресурсы, поиск, бронь, показатели и аудит; основа доступа CMP-009 уже есть. | 容器 HTTP 8000；本地绑定 127.0.0.1:8000 → 8000。基础 API 为 /api/v1/health、ready、docs。内部模块为进程内调用。<br>HTTP 8000 контейнера; локально 127.0.0.1:8000 → 8000. Базовые API: /api/v1/health, ready, docs. Вызовы внутренних модулей идут в одном процессе. | 本地容器候选<br>APP_ENV=<br>development<br>业务待实现<br>Локальный вариант контейнеров<br>APP_ENV=<br>development<br>Бизнес не реализован |

| N-05<br>HTTPS 入口<br>Вход HTTPS | 目标容器<br>Caddy<br>Целевой контейнер<br>Caddy | 目标制品为 Caddy 反向代理配置、证书及其持久存储；对接前端静态服务与 /api 路由。ADR-0004 已选定该技术方向。<br>Целевые артефакты: конфигурация обратного прокси Caddy, сертификаты и постоянное хранилище; доступ к статике клиента и маршрутам /api. Направление выбрано ADR-0004. | 目标 TCP 80 HTTP；<br>TCP 443 HTTPS/TLS。内部转发至前端 80 或后端 8000。具体路由与绑定随生产配置确定。<br>Целевые TCP 80 HTTP и TCP 443 HTTPS/TLS; внутри — порт 80 клиента либо 8000 сервера. Маршруты и привязки определяются производственной конфигурацией. | 目标部署方案<br>尚未执行<br>OPEN-010<br>Целевая схема<br>Не выполнено<br>OPEN-010 |

| N-06<br>目标数据库服务<br>Целевой сервис БД | 目标容器<br>PostgreSQL<br>Целевой контейнер<br>PostgreSQL | 承载业务数据库及持久数据卷。CMP-009 的 SQLAlchemy 层仍在 N-04，通过驱动访问此处数据；业务表与迁移待实现。<br>Размещает бизнес-БД и постоянный том. Слой SQLAlchemy CMP-009 остаётся в N-04 и обращается сюда через драйвер; бизнес-таблицы и миграции ещё предстоят. | PostgreSQL/TCP，连接示例为 5432；目标为内部网络访问。最终服务名、端口及绑定待生产配置确定。<br>PostgreSQL/TCP, в примере порт 5432; целевой доступ — во внутренней сети. Имя сервиса, порт и привязки задаются при подготовке размещения. | 目标部署方案<br>当前 Compose 未包含<br>迁移未执行<br>Целевая схема<br>В текущем Compose отсутствует<br>Миграция не выполнена |

| N-07<br>学校核验来源<br>Источник проверки вуза | 外部依赖<br>承载形式待定<br>Внешний источник<br>Тип уточняется | CMP-010：学校确认的名单或平台，为管理员人工核验提供依据；学校负责维护。StudySpace 内部记录必要来源引用及审核决定。<br>CMP-010: подтверждённый вузом реестр или платформа для ручной проверки администратором; поддерживается вузом. StudySpace сохраняет необходимые ссылки и решение. | IF-04 为人工核验依赖；具体渠道和端口待学校确认，未定义自动 API。<br>IF-04 — зависимость ручной проверки; канал и порты определяет вуз, автоматический API не определён. | 学校外部环境<br>OPEN-003<br>PARTIAL<br>Внешняя среда вуза<br>OPEN-003<br>PARTIAL |



## 节点与组件关系 / Связь узлов и компонентов

N-02 是直接启动方式，N-03 与 N-04 是另一种本地容器方式；它们不是必须同时运行的多套服务。CMP-001 由 N-03 分发并在 N-01 浏览器执行；CMP-002 至 CMP-009 在同一后端部署边界内，不为各业务模块单独增加服务端口。

N-02 — прямой локальный запуск, N-03 и N-04 — альтернативный запуск в контейнерах; одновременная работа обеих схем не требуется. CMP-001 раздаётся из N-03 и исполняется в браузере N-01; CMP-002–CMP-009 находятся в одной границе сервера без отдельных портов каждого модуля.



## 数据库制品与持久化 / Артефакты БД и сохранение данных

本地容器的 SQLite 文件为 /app/backend/data/studyspace.db，studyspace-data 卷挂载到 /app/backend/data；它是 N-04 内访问的文件制品，不是独立数据库服务器。目标 PostgreSQL 替代该存储方式，迁移、回滚、并发与恢复须分别验证；Alembic 尚待引入。

Файл SQLite локального контейнера — /app/backend/data/studyspace.db; том studyspace-data подключён к /app/backend/data. Это файловый артефакт N-04, а не отдельный сервер БД. Целевой PostgreSQL заменяет эту схему; миграция, откат, конкуренция и восстановление проверяются отдельно, Alembic ещё предстоит добавить.



## 环境与实施状态 / Среда и состояние реализации

当前 Compose 为 development 的本地 HTTP 配置，不包含 Caddy 或 PostgreSQL。目标部署状态为 NOT_EXECUTED，服务器、域名与具体生产配置仍受 OPEN-010 约束。现有基础 API 不等于预约业务已完成；容器部署、HTTPS、数据库迁移与业务验收未据本表确认，业务用例保持 NOT_RUN。学校核验来源仍为 OPEN-003，不能据此假定已有 SSO 或自动 API。

Текущий Compose — локальная конфигурация HTTP для development без Caddy и PostgreSQL. Статус целевого размещения NOT_EXECUTED; сервер, домен и производственная конфигурация связаны с OPEN-010. Базовые API не означают готовую бронь; таблица не подтверждает развёртывание контейнеров, HTTPS, миграцию или бизнес-приёмку, бизнес-кейсы остаются NOT_RUN. Источник вуза остаётся OPEN-003; готовые SSO и автоматический API не предполагаются.



## 项目依据 Источники проекта

- S1: /Users/zhi/Documents/软件生命周期/studyspace/docs/zh-CN/04_System_Design.md

- S2: /Users/zhi/Documents/软件生命周期/studyspace/docs/ru-RU/04_System_Design.md

- S3: /Users/zhi/Documents/软件生命周期/studyspace/compose.yaml

- S4: /Users/zhi/Documents/软件生命周期/studyspace/frontend/Dockerfile

- S5: /Users/zhi/Documents/软件生命周期/studyspace/frontend/nginx.conf

- S6: /Users/zhi/Documents/软件生命周期/studyspace/backend/Dockerfile

- S7: /Users/zhi/Documents/软件生命周期/studyspace/scripts/dev.sh

- S8: /Users/zhi/Documents/软件生命周期/studyspace/frontend/vite.config.ts

- S9: /Users/zhi/Documents/软件生命周期/studyspace/backend/app/config.py

- S10: /Users/zhi/Documents/软件生命周期/studyspace/backend/app/main.py

- S11: /Users/zhi/Documents/软件生命周期/studyspace/backend/app/database.py

- S12: /Users/zhi/Documents/软件生命周期/studyspace/.env.example

- S13: /Users/zhi/Documents/软件生命周期/studyspace/docs/data/project-decisions.json

- S14: /Users/zhi/Documents/软件生命周期/studyspace/docs/decisions/zh-CN/0004-docker-https.md

- S15: /Users/zhi/Documents/软件生命周期/studyspace/docs/decisions/ru-RU/0004-docker-https.md

- S16: /Users/zhi/Documents/软件生命周期/studyspace/coursework/2026-10-14-architecture-decisions-v1/StudySpace_两份ADR架构决策记录_中俄双语_v1.md

- S17: /Users/zhi/Documents/软件生命周期/StudySpace_组件交付/StudySpace_组件候选与组件图_中俄双语_v2.md

- S18: /Users/zhi/Documents/软件生命周期/studyspace/backend/pyproject.toml

- S19: /Users/zhi/Documents/软件生命周期/studyspace/AGENTS.md
