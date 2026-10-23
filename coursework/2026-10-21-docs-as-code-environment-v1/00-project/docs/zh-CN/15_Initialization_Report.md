# StudySpace 项目初始化报告

| Key | Value |
| --- | --- |
| Doc-ID | DOC-15 |
| Version | 0.3.0 |
| Status | DRAFT |
| Updated | 2026-10-12 |
| Language | zh-CN |

第1–7章为应用0.1.0首次初始化的历史证据，保留当时文件数、测试数和未决情况；第8章保留0.2.0澄清历史；当前0.3.0规则及课堂角色见第9章和16_Requirements_Clarification.md。

## 1. 交付位置与范围

项目路径：`/Users/zhi/Documents/软件生命周期/studyspace`。本次仅初始化工程基础；认证、角色权限、房间管理、预约、冲突处理、取消和统计等业务尚未实现。SRS是草稿模板，需求是待确认候选，测试用例是计划，未执行用户调研、正式批准或业务验收。现有项目外3份课程源文件在初始化前后SHA-256一致。

## 2. 实际环境与架构

| 项目 | 实测环境或决策 |
| --- | --- |
| Git | 2.54.0 (Apple Git-157)，本地 main，无提交和远程 |
| Node / npm | v26.0.0 / 11.12.1；项目支持22.13+（22.x）或24+ |
| Python | 系统默认3.14.5；本项目实际使用3.13.12 |
| uv | 0.11.17 |
| Docker / Compose | 29.8.0 / v5.5.1；CLI可用，守护进程未运行 |
| 前端 | React18.3.1 / TypeScript5.9.3 / Vite7.3.7 / Ant Design5.29.3 |
| 后端 | FastAPI0.143.0 / SQLAlchemy2.0.54 / Pydantic2.14.1 |
| 测试与检查 | pytest9.1.1 / Vitest4.1.11 / ESLint10.12.0 / ruff0.17.0 |

采用前后端分离的模块化单体，HTTP/JSON接口、Pydantic校验、同步SQLAlchemy及开发SQLite。PostgreSQL可选驱动已预留，尚未安装该可选组或完成迁移验证。数据库就绪仅检查`SELECT 1`；SQLite文件无业务表。后端只有`/api/v1/health`、`/api/v1/ready`，文档与Schema在`/api/v1/docs`、`/api/v1/openapi.json`。

## 3. 已执行检查与证据

| 检查 | 实际结果 | 证据 |
| --- | --- | --- |
| 冻结依赖安装 | 根setup脚本成功；uv虚拟环境、npm ci成功 | `artifacts/setup.log` |
| 后端基础测试 | 8 passed | 后端pytest输出；最终整体验证见`artifacts/check.log` |
| 前端基础测试 | 16 passed，2个测试文件 | 前端Vitest输出；最终整体验证见`artifacts/check.log` |
| 文档结构与追溯 | 18对正式文档结构、元数据、编号、JSON引用和生成区块一致性检查通过 | `scripts/check_docs.py` |
| 根目录文档校验测试 | 8 passed；与后端合计pytest 16 passed | `tests/test_documentation.py` |
| 类型、lint、格式、构建 | 根check脚本整体验证通过 | `scripts/check.sh` |
| npm依赖审查 | 0个已知漏洞（审查时点结果） | `artifacts/npm-audit.json` |
| 联合启动与HTTP | 根dev脚本已启动两服务；直接/代理health、ready、OpenAPI和Swagger HTML通过 | `artifacts/http-smoke.log` |
| 浏览器渲染 | 中文和俄语实际显示连接成功；375px俄语无横向溢出；本地重新加载控制台无错误 | `artifacts/browser-home-zh.json`、`artifacts/browser-home-ru-mobile.json`、`artifacts/browser-console.log` |
| Compose配置 | `docker compose config --quiet`通过 | CLI执行结果；容器未构建启动 |

实际浏览器截图：`artifacts/screenshots/home-zh.png`、`home-ru.png`、`home-ru-mobile.png`。测试日志与截图在本机保留，并由.gitignore排除。骨架测试和页面检查不能替代业务测试或验收；所有计划业务TC仍为NOT_RUN。

已知工具提示：Starlette TestClient的httpx集成发出弃用警告；npm的间接依赖whatwg-encoding发出弃用提示。没有隐藏这些提示，它们不代表本次测试失败。首次烟雾脚本首页URL缺少末尾`/`导致400，修正后复验通过；首次日志保留在`artifacts/http-smoke-first-attempt.log`。

## 4. 创建文件与工程管理

完整实际源文件清单：[`../file-inventory.txt`](../file-inventory.txt)。此清单排除Git内部文件、虚拟环境、node_modules、缓存、构建产物及运行数据库。正式文档共18对（15对课程文档与3对ADR），全部0.1.0/DRAFT；37条需求全部PROPOSED，37个业务TC全部NOT_RUN。额外本地产物为`.env`、`backend/.venv/`、`frontend/node_modules/`、`frontend/dist/`、`backend/data/studyspace.db`及`artifacts/`证据。

工程包含README、AGENTS、CHANGELOG、环境变量示例、可选Compose、前后端配置/源码/测试、安装与开发脚本、中俄正式草稿、JSON登记来源、文档manifest及成对ADR。需求/测试用例编号稳定。执行`python3 scripts/generate_registers.py`仅更新两个语言的需求登记与追溯矩阵指定生成区块；`--check`只检查，不写文件。正式批准、语义翻译准确性和需求合理性仍需团队人工评审。

## 5. 本地运行

```bash
cd "/Users/zhi/Documents/软件生命周期/studyspace"
bash scripts/setup.sh
bash scripts/dev.sh
```

首页：`http://127.0.0.1:5173/`；API文档：`http://127.0.0.1:8000/api/v1/docs`。联合启动后已实际用`Ctrl+C`停止两服务，并核实8000与5173均不再监听；交付时开发服务未运行。开发时运行`bash scripts/check.sh`；两服务运行时可执行`backend/.venv/bin/python scripts/smoke_http.py`。首次依赖下载需要网络；自定义Python可通过`STUDYSPACE_PYTHON`指定。

## 6. 尚未完成与待确认

- OPEN-001：团队4人规模与A/B/C三人分工的冲突待确认。
- 身份来源、角色授予、开放时段、预约边界、时区、取消条件、统计范围及并发策略待确认。
- 全部业务实现、业务测试、最终SRS、真实用户调研、正式验收及PostgreSQL迁移未完成。
- Docker守护进程未运行，因此镜像构建与容器启动未验证。
- Git尚未提交，也未设置远程或推送；GitHub协作、课程批准及开源许可证留待确认。

## 7. 下一步建议

先由团队和课程负责人处理待确认事项，评审候选需求及中俄术语，再形成批准的需求基线。按8周计划依次完成认证与RBAC、资源与开放时段、服务端事务内预约冲突/取消、管理员流程，最后执行计划业务测试和课程验收。座位、提醒、二维码、违约和使用率统计不得挤占MVP。每个功能同步需求、设计、实现路径与真实测试证据。

## 8 需求澄清0.2.0与本轮验证

用户答复已确认四人实名、单座位MVP、校内核验要求、最长一天/每人一个座位、老师验收、三语界面，并授权其他规则。见16_Requirements_Clarification.md及project-decisions.json；默认每天08:00–22:00、30分钟粒度、24h硬上限、每人最多1条未结束预约含未来、Asia/Shanghai及7自然日窗口。12项设计问题CLOSED，3项外部条件PARTIAL。FR-017/TC-017保留ID升MVP，新增FR-022/TC-038；当前38条需求均PROPOSED、38个业务TC均NOT_RUN，20对正式文档均0.2.0/DRAFT。

本轮实际运行根check：pytest18 passed（后端8+文档10），Vitest19 passed；双语结构/ID/生成区块/决策引用、ruff/格式、ESLint、TypeScript、构建和Compose配置通过。日志artifacts/clarification-check.log；文档最终更新检查见artifacts/clarification-doc-final.log。未执行计划业务用例，也未创建业务表、做迁移或验收。

实际本地浏览器分别显示zh-CN/ru-RU/en-US且连接成功；英语375px无横向溢出，本轮控制台无错误。截图artifacts/screenshots/clarification-home-en.png和clarification-home-en-mobile.png，检查artifacts/clarification-browser.jsonl、clarification-browser-console.log；HTTP合同/SQLite/代理检查artifacts/clarification-http-smoke.log。联合启动后已停止8000/5173，证据clarification-service-stop.log。应用与健康合同仍0.1.0，本轮未改变依赖或锁文件，无推送、部署、证书申请或真实校内核验。

## 9 预约纠正与课堂角色0.3.0

DEC-016把旧全局未结束预约总数限制改为同学生时间区间互斥，非重叠同日、不同未来日及相邻时段允许多条，每条仍1seat。DEC-017按附图四角色和名单顺序：支浩然分析员/技术任务书作者，俞智文文档编辑，曹浩然测试员，吕嘉伟项目经理；可按主题轮换交接。原图docs/assets/classroom-role-assignment.jpg。

需求/TC编号保持稳定，38业务TC仍NOT_RUN，业务未实现。三语首页文案已同步；本轮实际检查pytest20项（后端8+文档12）、Vitest19项通过，双语/编号/生成区块、lint、类型和构建通过；见artifacts/interval-role-check.log和interval-role-doc-final.log，不能当业务验收。第8章旧总量解释作为0.2.0历史保留，已被本章新规则替代。
