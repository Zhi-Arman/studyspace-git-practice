# StudySpace：3.4.4 环境与材料准备 / Среда и материалы 3.4.4

Version: 0.4 · Status: DRAFT / PARTIAL_MATERIALS · Date: 2026-10-21 · Timezone: Asia/Shanghai

已按照片中第 1 部分完成本地环境核查和现有材料整理。Python 与依赖安装能力通过检查；材料仍有明确缺口，见下表。本目录是独立学习副本，原 StudySpace 文档、依赖环境和数据库保持原状。

Выполнены локальная проверка среды и сбор имеющихся материалов по первой части задания на фото. Python и возможность установки зависимостей проверены; пробелы материалов указаны ниже. Это отдельная учебная копия; исходные документы, среда и БД StudySpace сохранены.

## 1 课堂要求对照 / Соответствие заданию

| 图片要求 / Требование | 结果 / Результат | 入口 / Материал |
| --- | --- | --- |
| 打开起始文档项目压缩包 / Открыть стартовый архив | PARTIAL：未找到教师原包；已生成并校验本地快照，不能替代原包身份 / Архив преподавателя не найден; локальный снимок проверен, но не является оригиналом | [本地快照 ZIP / Локальный ZIP](00-studyspace-local-snapshot.zip)、[已展开副本 / Распакованная копия](00-project/SNAPSHOT_SCOPE.md) |
| Python 3.11+、可安装依赖 / Python 3.11+ и установка зависимостей | PASS：Python 3.13.12；46 个锁定依赖安装成功、兼容性及导入通过 / Установлены 46 пакетов по lock-файлу, совместимость и импорт проверены | [环境报告 / Отчёт среды](环境检查报告.md) |
| 部署图、节点与环境表、ADR、需求 / Диаграмма, узлы, среды, ADR, требования | PARTIAL：表格、ADR、需求已收齐；独立部署图原件未找到，已根据既有资料补充 DRAFT 草案 / Таблицы, ADR и требования собраны; исходная диаграмма не найдена, подготовлен DRAFT | [部署图草案 / Черновик диаграммы](01-deployment/部署图说明.md)、[材料目录 / Перечень](#2-材料目录--перечень-материалов) |
| 3.4.3 指南及意见清单 / Руководство 3.4.3 и замечания | 指南对应关系 CONFIRMED_BY_USER（2026-10-21）；原始意见清单 MISSING，因此该组合项仍 PARTIAL / Соответствие руководств CONFIRMED_BY_USER (21.10.2026); исходные замечания MISSING, общий пункт PARTIAL | [已确认指南与缺口说明 / Подтверждённые руководства и пробелы](05-guide-3.4.3/README.md)、[登记表 / Реестр](05-guide-3.4.3/remarks-register.md) |
| 独立学习目录，不用生产服务器 / Отдельная папка без продакшена | PASS：仅在本目录创建副本和虚拟环境，未启动服务或访问生产服务器 / Созданы только учебные копии и среда; сервисы и продакшен не использовались | 本目录 / Этот каталог |

## 2 材料目录 / Перечень материалов

- `00-project/`：当前项目源码与文档快照；包含锁文件，不含原 .env、数据库、.git、依赖目录与旧 coursework。详见 [快照范围](00-project/SNAPSHOT_SCOPE.md)。
  Снимок исходников и документов с lock-файлами; без исходного .env, БД, .git, зависимостей и прежнего coursework. См. [границы](00-project/SNAPSHOT_SCOPE.md).
- `01-deployment/`：[部署图说明及 Mermaid 草案](01-deployment/部署图说明.md)、[既有部署图检查表](01-deployment/StudySpace_部署图检查表_中俄双语_v1.md)和同名 Word。
  [Описание и черновики Mermaid](01-deployment/部署图说明.md), [прежний контрольный список](01-deployment/StudySpace_部署图检查表_中俄双语_v1.md) и Word.
- `02-nodes-environments/`：[节点与制品表](02-nodes-environments/StudySpace_节点与制品表_中俄双语_v1.md)、[环境与防护表](02-nodes-environments/StudySpace_环境与防护表_中俄双语_v1.md)，均有原样 Word 副本。
  [Узлы и артефакты](02-nodes-environments/StudySpace_节点与制品表_中俄双语_v1.md), [среды и защита](02-nodes-environments/StudySpace_环境与防护表_中俄双语_v1.md) с неизменёнными копиями Word.
- `03-adr/`：[ADR-0001—ADR-0004 中俄源文件](03-adr/README.md)及 `coursework/` 下两份 ADR 的历史汇总 Markdown / Word。
  [Парные исходники ADR-0001–ADR-0004](03-adr/README.md) и прежняя сводка двух ADR в `coursework/`.
- `04-requirements/current/`：[当前中文 SRS](04-requirements/current/zh-CN/03_SRS_IEEE830.md)、[俄文 SRS](04-requirements/current/ru-RU/03_SRS_IEEE830.md)、澄清、登记、追溯、问题清单和 JSON；`historical-v0.2/` 的 Word / Excel / Markdown 仅作历史课程材料。
  [Текущая SRS на китайском](04-requirements/current/zh-CN/03_SRS_IEEE830.md), [на русском](04-requirements/current/ru-RU/03_SRS_IEEE830.md), уточнения, реестры, трассировка, вопросы и JSON. Word / Excel / Markdown в `historical-v0.2/` — исторические учебные материалы.
- `05-guide-3.4.3/`：[两份已确认对应 3.4.3 的指南与缺失清单](05-guide-3.4.3/README.md)。
  [Два подтверждённых руководства 3.4.3 и пробелы](05-guide-3.4.3/README.md).
- `artifacts/`：[完整来源及 SHA-256 清单](artifacts/materials-manifest.json)、[复制核验](artifacts/copy-verification.json)、[环境实测 JSON](artifacts/environment-check.json)及安装、兼容性、文档检查日志。
  [Источники и SHA-256](artifacts/materials-manifest.json), [проверка копий](artifacts/copy-verification.json), [среда JSON](artifacts/environment-check.json) и журналы установки, совместимости и документов.
- `.venv/`：本次新建的独立 Python 环境，46 个依赖；不是原 `backend/.venv`。
  Новая отдельная среда Python с 46 пакетами, отличная от исходной `backend/.venv`.

学习副本中的完整 `00-project/docs/` 保留原始相对结构，适合继续编辑；分类副本用于快速取用，继承的文内链接可能仍依赖原项目结构。正式文件依旧 DRAFT，38 条需求为 PROPOSED，38 个业务用例仍 NOT_RUN。历史 v0.2 不覆盖当前 0.3.0 规则。

В `00-project/docs/` сохранена полная структура для дальнейшего редактирования; тематические копии удобны для поиска, но их прежние ссылки могут зависеть от исходной структуры. Документы остаются DRAFT, 38 требований PROPOSED, 38 бизнес-кейсов NOT_RUN. Историческая v0.2 не заменяет текущие правила 0.3.0.

## 3 复核命令 / Команды проверки

在本学习目录执行： / Выполнять из этой учебной папки:

```bash
cd '/Users/zhi/Documents/软件生命周期/studyspace/coursework/2026-10-21-docs-as-code-environment-v1'
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python 00-project/scripts/check_docs.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python 00-project/scripts/generate_registers.py --check
UV_CACHE_DIR="$PWD/artifacts/uv-cache" uv pip check --python .venv/bin/python
```

如需按锁文件再次同步学习环境（可能访问包下载网络）：

Для повторной синхронизации среды по lock-файлу (может потребоваться сеть загрузки пакетов):

```bash
UV_PROJECT_ENVIRONMENT="$PWD/.venv" UV_CACHE_DIR="$PWD/artifacts/uv-cache" \
  uv sync --project 00-project/backend --python 3.13 --frozen --no-python-downloads
```

本次只验证现有后端依赖；教师原始文档项目及其依赖未提供，不能声称已验证 MkDocs、Sphinx 或后续未展示步骤。无需为本次准备任务运行 setup.sh、dev.sh、Compose、数据库迁移或业务测试。

Проверены зависимости имеющегося бэкенда; исходный проект документации преподавателя и его зависимости отсутствуют. Проверка MkDocs, Sphinx и следующих невидимых шагов не заявляется. Для этой подготовки не требуется запускать setup.sh, dev.sh, Compose, миграции или бизнес-тесты.

## 4 第 2 部分 从架构推导操作指南

## 4 Часть 2 Руководство на основе архитектуры

已在同一学习文件夹新增 [第 2 部分交付目录](06-architecture-guide/README.md)，包含 [中俄双语 Word](06-architecture-guide/StudySpace_任务二从架构推导操作指南_中俄双语_v1.docx) 和 [Markdown](06-architecture-guide/StudySpace_任务二从架构推导操作指南_中俄双语_v1.md)。覆盖 10 个组件、7 个节点的 28 项操作属性及来源、10 章指南大纲和 10 项验证流程。

В этом учебном пакете добавлен [результат части 2](06-architecture-guide/README.md): [двуязычный Word](06-architecture-guide/StudySpace_任务二从架构推导操作指南_中俄双语_v1.docx) и [Markdown](06-architecture-guide/StudySpace_任务二从架构推导操作指南_中俄双语_v1.md). Охвачены 10 компонентов, 28 полей 7 узлов с источниками, 10 глав и 10 проверок.

第 2 部分新增已有基础测试 8 passed、1 warning 及 Compose 静态配置解析通过的记录；均在学习副本执行，没有启动容器或网络服务。完整执行证据和未执行边界见 [execution.json](06-architecture-guide/artifacts/execution.json)。第 1 部分报告保留其原检查范围和时间。

В части 2 добавлены свидетельства 8 passed, 1 warning существующих тестов и успешного разбора Compose. Проверки в учебной копии, без запуска контейнеров и сетевых сервисов. Команды и границы — в [execution.json](06-architecture-guide/artifacts/execution.json). Отчёт части 1 сохраняет свою область и дату проверки.

## 5 第 3 部分 管理员指南

## 5 Часть 3 Руководство администратора

已完成 [admin-guide.md](admin-guide.md) 和 [中俄双语 Word](StudySpace_管理员指南_中俄双语_v1.docx)：8 个主要章节，另加限制和变更历史；4 个流程、9 个配置项、6 种诊断场景。依据、模板说明、恢复工具和验证记录见 [第 3 部分交付说明](07-admin-guide/README.md)。

Готовы [admin-guide.md](admin-guide.md) и [двуязычный Word](StudySpace_管理员指南_中俄双语_v1.docx): 8 основных глав, ограничения и история, 4 процедуры, 9 параметров и 6 ситуаций диагностики. Источники, пояснение шаблона, инструмент и проверки — в [описании части 3](07-admin-guide/README.md).

恢复演练仅使用两条合成记录，备份和恢复候选完整性检查通过，原文件未变，重复输出和包外路径被拒绝；未激活候选或执行真实业务恢复。原有缺失材料和业务 NOT_RUN 状态保持不变。

В упражнении восстановлены две синтетические записи; целостность копии и кандидата проверена, исходник сохранён, повторные файлы и внешние пути отклонены. Кандидат не активирован, бизнес-восстановление не выполнялось. Пробелы материалов и бизнес-NOT_RUN сохранены.

## 6 第 4 部分 Sphinx 文档站

## 6 Часть 4 Сайт документации Sphinx

新增 [project-docs 交付目录](08-sphinx-site/project-docs/README.md)：按新提供的九章模板形成管理员手册 v0.2，五个六字段流程卡；保留 3.4.3 用户指南并补发布说明、文档登记、构建证据和自查。入口为 [本地网站](08-sphinx-site/project-docs/site/index.html)、[中俄 Word](08-sphinx-site/project-docs/StudySpace_管理员手册_中俄双语_v0.2.docx) 和 [管理员 Markdown](08-sphinx-site/project-docs/docs/admin-guide.md)。原 v0.1 文件保留。

Добавлен [каталог project-docs](08-sphinx-site/project-docs/README.md): руководство 0.2 по девяти главам нового фото, пять процедур с шестью полями; сохранено руководство 3.4.3, добавлены примечания, реестр, сборка и самопроверка. Вход: [локальный сайт](08-sphinx-site/project-docs/site/index.html), [Word](08-sphinx-site/project-docs/StudySpace_管理员手册_中俄双语_v0.2.docx), [Markdown](08-sphinx-site/project-docs/docs/admin-guide.md). Исходная 0.1 сохранена.

独立 .venv 安装 28 个锁定文档依赖；Sphinx 严格构建警告 0，88 项检查及 250 处本地链接检查通过，22 份源文件哈希不变。12 页 Word 已逐页查看；浏览器验证目录、搜索和下载。证据见 [build-evidence.md](08-sphinx-site/project-docs/build-evidence.md)。只运行文档站，未运行应用业务、升级或生产恢复；教师原包和原始意见仍缺失。

В отдельной .venv 28 фиксированных пакетов; строгая сборка без предупреждений, 88 проверок и 250 локальных ссылок пройдены, хеши 22 источников сохранены. Просмотрены 12 страниц Word; в браузере проверены меню, поиск и скачивание. См. [свидетельства](08-sphinx-site/project-docs/build-evidence.md). Работал только сайт документации, без бизнес-приложения, обновления или продакшен-восстановления; исходный архив и замечания отсутствуют.

## 7 第 5 部分 网站与构建检查

## 7 Часть 5 Проверка сайта и сборки

已完成新图六项要求，见 [第 5 部分交付说明](09-site-build-check/README.md)、[中俄 Word 报告](09-site-build-check/StudySpace_任务五网站与构建检查_中俄双语_v1.docx) 与 [Markdown](09-site-build-check/StudySpace_任务五网站与构建检查_中俄双语_v1.md)。两轮严格构建均退出 0、警告 0；从目录实际点击四页，完成含图片与标题的 8 项链接或资源检查；13 项浏览器检查、27 项报告验证通过。四页 Word 已逐页查看。独立 SVG 快照工具超时的处理及复测保留原始证据；网站源码未修改，应用命令保持本轮 NOT_RUN。

Выполнены шесть требований нового фото: [описание части 5](09-site-build-check/README.md), [Word](09-site-build-check/StudySpace_任务五网站与构建检查_中俄双语_v1.docx), [Markdown](09-site-build-check/StudySpace_任务五网站与构建检查_中俄双语_v1.md). Обе строгие сборки: код 0, предупреждений 0; из оглавления открыты четыре страницы, выполнены 8 проверок ссылок/ресурсов с изображением и заголовком. Пройдены 13 проверок браузера и 27 проверок отчёта. Просмотрены четыре страницы Word. Сохранены тайм-аут snapshot SVG, исправление и повторный результат; исходники сайта не изменены, команды приложения сейчас NOT_RUN.
