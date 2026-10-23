# StudySpace 文档管理 / Управление документацией

本目录保存中俄正式文档的对应草稿；导航文件不作为另一个需求基线。Официальные черновики представлены в китайско-русских парах; навигационные файлы не создают отдельную базу требований.

## 1 目录 / Каталог

| Doc-ID | zh-CN | ru-RU | Version | Status |
| --- | --- | --- | --- | --- |
| DOC-01 | [中文](zh-CN/01_Project_Charter.md) | [Русский](ru-RU/01_Project_Charter.md) | 0.3.0 | DRAFT |
| DOC-02 | [中文](zh-CN/02_Project_Concept.md) | [Русский](ru-RU/02_Project_Concept.md) | 0.3.0 | DRAFT |
| DOC-03 | [中文](zh-CN/03_SRS_IEEE830.md) | [Русский](ru-RU/03_SRS_IEEE830.md) | 0.3.0 | DRAFT |
| DOC-04 | [中文](zh-CN/04_System_Design.md) | [Русский](ru-RU/04_System_Design.md) | 0.3.1 | DRAFT |
| DOC-05 | [中文](zh-CN/05_Test_Plan.md) | [Русский](ru-RU/05_Test_Plan.md) | 0.3.1 | DRAFT |
| DOC-06 | [中文](zh-CN/06_Test_Cases.md) | [Русский](ru-RU/06_Test_Cases.md) | 0.3.0 | DRAFT |
| DOC-07 | [中文](zh-CN/07_Traceability_Matrix.md) | [Русский](ru-RU/07_Traceability_Matrix.md) | 0.3.0 | DRAFT |
| DOC-08 | [中文](zh-CN/08_Risk_Register.md) | [Русский](ru-RU/08_Risk_Register.md) | 0.3.0 | DRAFT |
| DOC-09 | [中文](zh-CN/09_Change_Log.md) | [Русский](ru-RU/09_Change_Log.md) | 0.3.1 | DRAFT |
| DOC-10 | [中文](zh-CN/10_User_Manual.md) | [Русский](ru-RU/10_User_Manual.md) | 0.3.0 | DRAFT |
| DOC-11 | [中文](zh-CN/11_Development_Plan.md) | [Русский](ru-RU/11_Development_Plan.md) | 0.3.0 | DRAFT |
| DOC-12 | [中文](zh-CN/12_Open_Questions.md) | [Русский](ru-RU/12_Open_Questions.md) | 0.3.0 | DRAFT |
| DOC-13 | [中文](zh-CN/13_Glossary.md) | [Русский](ru-RU/13_Glossary.md) | 0.3.0 | DRAFT |
| DOC-14 | [中文](zh-CN/14_Requirements_Register.md) | [Русский](ru-RU/14_Requirements_Register.md) | 0.3.0 | DRAFT |
| DOC-15 | [中文](zh-CN/15_Initialization_Report.md) | [Русский](ru-RU/15_Initialization_Report.md) | 0.3.0 | DRAFT |
| DOC-16 | [中文](zh-CN/16_Requirements_Clarification.md) | [Русский](ru-RU/16_Requirements_Clarification.md) | 0.3.0 | DRAFT |
| DOC-17 | [中文](zh-CN/17_API_Contract.md) | [Русский](ru-RU/17_API_Contract.md) | 0.1.0 | DRAFT |
| ADR-0001 | [中文](decisions/zh-CN/0001-simple-monolith.md) | [Русский](decisions/ru-RU/0001-simple-monolith.md) | 0.3.0 | DRAFT |
| ADR-0002 | [中文](decisions/zh-CN/0002-sqlite-postgresql.md) | [Русский](decisions/ru-RU/0002-sqlite-postgresql.md) | 0.3.0 | DRAFT |
| ADR-0003 | [中文](decisions/zh-CN/0003-room-level-mvp.md) | [Русский](decisions/ru-RU/0003-room-level-mvp.md) | 0.3.0 | DRAFT |

| ADR-0004 | [中文](decisions/zh-CN/0004-docker-https.md) | [Русский](decisions/ru-RU/0004-docker-https.md) | 0.3.0 | DRAFT |

登记补充（2026-10-21）：DOC-17 的配套机器可读契约为 [docs/api/openapi.yaml](api/openapi.yaml)。登记状态 DRAFT 与静态契约校验通过不代表业务端点已经实现；业务测试仍为 NOT_RUN。

Уточнение реестра (2026-10-21): машиночитаемый контракт DOC-17 находится в [docs/api/openapi.yaml](api/openapi.yaml). Состояние DRAFT и успешная статическая проверка не означают реализацию бизнес-API; бизнес-тесты остаются NOT_RUN.

## 2 命名与元数据 / Имена и метаданные

正式文档按zh-CN/与ru-RU/成对；01至17保持相同文件名，ADR放decisions/zh-CN/与decisions/ru-RU/。manifest.json登记正式文件、版本、状态和纯数字章节编号；新增正式文件需先在两语创建，再登记清单。

Документы образуют пары в zh-CN/ и ru-RU/ с одинаковыми именами. ADR находятся в decisions/zh-CN/ и decisions/ru-RU/. manifest.json содержит пары, версию, состояние и цифровые номера разделов. Новый официальный документ создаётся на обоих языках и добавляется в manifest.

每份正式文件使用英文元数据key：Doc-ID、Version、Status、Updated、Language。需求登记版本仍0.3.0；各文档Version及Updated以manifest的条目为准，Status=DRAFT；Language分别zh-CN或ru-RU。技术ADR另用Decision-Status，避免将技术选定等同文档终审。

Каждый документ содержит ключи Doc-ID, Version, Status, Updated, Language. Версия реестров остаётся0.3.0; Version и Updated документа задаются его записью manifest, Status=DRAFT; Language равен zh-CN либо ru-RU. Для ADR отдельно используется Decision-Status, чтобы не смешивать технический выбор с утверждением документа.

## 3 稳定编号 / Стабильные идентификаторы

| 前缀 / Префикс | 含义 / Значение | 规则 / Правило |
| --- | --- | --- |
| FR-001 | 功能需求 / Функциональное требование | 递增，不重用 / Возрастание, без повторного использования |
| NFR-001 | 非功能需求 / Нефункциональное требование | 递增，不重用 / Возрастание, без повторного использования |
| BR-001 | 业务规则 / Бизнес-правило | 递增，不重用 / Возрастание, без повторного использования |
| TC-001 | 测试用例 / Тестовый сценарий | 递增，不重用 / Возрастание, без повторного использования |
| RISK-001 | 风险 / Риск | 递增，不重用 / Возрастание, без повторного использования |
| OPEN-001 | 待确认 / Открытый вопрос | 递增，不重用 / Возрастание, без повторного использования |
| ADR-0001 | 架构决策 / Архитектурное решение | 递增，不重用 / Возрастание, без повторного использования |

章节重排不修改ID；取消或否决的条目保留ID、状态与理由。Перестановка разделов не меняет ID; снятые или отклонённые записи сохраняют ID, состояние и причину.

## 4 源与生成 / Источники и генерация

data/requirements.json为双语候选登记来源，data/test-cases.json为双语计划测试来源，data/project-decisions.json保存用户确认及授权制定的规则输入。06、07与14文档的GENERATED:BEGIN/END区块由这些源产生，其他章节人工维护。修改源后通过项目scripts/generate_registers.py重生成并运行scripts/check_docs.py；准确命令见根README。自动检查是结构证据，译文语义和需求正确性仍需人工审阅。

data/requirements.json задаёт двуязычный реестр кандидатов, data/test-cases.json — план тестов, data/project-decisions.json — подтверждённые и делегированные входные решения. Блоки GENERATED:BEGIN/END документов 06, 07 и 14 генерируются из источников; остальные разделы поддерживаются вручную. После изменения использовать scripts/generate_registers.py и scripts/check_docs.py по корневому README. Автоматизация проверяет структуру, смысл перевода и требований проверяется людьми.

## 5 状态、版本与审阅 / Состояния, версия и рассмотрение

DRAFT、PROPOSED、NOT_RUN分别是文档草稿、候选需求、未执行测试。缺少来源或未获得有权者批准时不得改为已确认。需求批准、实现、测试和验收独立记录，健康测试不代表业务TC通过。需求状态使用PROPOSED/APPROVED/IMPLEMENTED/VERIFIED/RETIRED；APPROVED及之后记录approval（approved_by、approved_at、evidence）；IMPLEMENTED及VERIFIED需要真实非空implementation，VERIFIED需要关联PASS且有证据的用例。

DRAFT, PROPOSED и NOT_RUN обозначают черновик, кандидат и невыполненный тест. Без источника и полномочного решения не устанавливается согласование. Утверждение, реализация, тестирование и приёмка записываются отдельно; проверка здоровья не означает прохождение бизнес-TC. Состояния требований: PROPOSED/APPROVED/IMPLEMENTED/VERIFIED/RETIRED. APPROVED и последующие состояния требуют approval (approved_by, approved_at, evidence); IMPLEMENTED и VERIFIED — фактические непустые связи implementation; VERIFIED — связанные PASS с доказательствами.

MAJOR.MINOR.PATCH：不兼容基线/范围变更、兼容扩展、修正。所有正式两语对应文档同时更新Version、Updated、章节、ID及语义，写入09变更记录，并请另一位成员审阅；版本相同不自动证明译文正确。课程其他版本规则待确认。

MAJOR.MINOR.PATCH: несовместимая база/объём, совместимое расширение, исправление. Пара обновляет Version, Updated, разделы, ID и смысл совместно; запись в журнале 09 рассматривает другой участник. Одинаковая версия сама по себе не доказывает перевод. Иные правила курса требуют подтверждения.

结构校验不证明审批人的身份或证据真实性，仍需团队审阅。

Структурная проверка не подтверждает личность согласующего или подлинность свидетельств; требуется рассмотрение командой.

## 6 编写依据 / Основание подготовки

SRS按课程指定IEEE Std 830-1998组织；[官方条目](https://standards.ieee.org/ieee/830/1222/)已核对，显示取代关系。未取得授权全文，未做逐条认证。其余文档按各自用途组织。不得编造调研、测试、验收或已批准业务参数。

SRS организуется по выбранному курсом IEEE Std 830-1998; [официальная запись](https://standards.ieee.org/ieee/830/1222/) проверена и показывает замену стандарта. Лицензированный полный текст не получен, поэлементная сертификация не выполнена. Остальные документы организуются по назначению. Исследования, тесты, приёмка и утверждённые бизнес-параметры не выдумываются.

业务API契约 / Контракт бизнес-API: [OpenAPI YAML](api/openapi.yaml) · [中文说明](zh-CN/17_API_Contract.md) · [Русское описание](ru-RU/17_API_Contract.md)。静态DRAFT；业务测试NOT_RUN / Статический DRAFT; бизнес-тесты NOT_RUN.
