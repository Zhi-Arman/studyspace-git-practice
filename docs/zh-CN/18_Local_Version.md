# StudySpace 本地课程版

| Metadata | Value |
| --- | --- |
| Doc-ID | DOC-18 |
| Version | 0.4.0 |
| Status | DRAFT |
| Updated | 2026-10-23 |
| Language | zh-CN |

## 1 当前范围

DEC-018：用户取消真实学校身份核验和远程部署要求。本地账号注册即可预约；身份模式LOCAL_ONLY。FR-022撤销，编号保留。

## 2 结构与运行

React/TypeScript + FastAPI/SQLAlchemy + SQLite/Alembic；本地Docker Compose为主要环境，保留原生脚本。只映射127.0.0.1，不依赖域名、HTTPS、外部字体或学校平台。

## 3 账号与预约规则

本地用户名/显示名，scrypt密码、可撤销HttpOnly会话，管理员显式创建且无默认密码。单次一个座位，同用户与座位[start,end)互斥，相邻和多条不重叠预约允许；上海时区、30分钟粒度、默认08:00–22:00和7自然日，最多24小时。

## 4 管理与数据

房间/座位、开放时间和日期例外、用户启停/角色、预约和基础统计。停用及缩短时间须事务取消受影响预约；最后管理员受保护。SQLite写事务使用BEGIN IMMEDIATE。维护命令提供保留期清理、备份和恢复到新文件。

## 5 测试与证据

本轮Python63项、前端23项自动化测试通过；实际Docker、重启持久化、原生启动与Chromium学生/管理流程已执行。证据见[本地执行报告](../evidence/local-v0.4/validation.md)。历史课程TC未逐条人工执行，仍保留NOT_RUN，不伪造批准。

## 6 历史材料与交付

已有0.3正式文档及课堂文件保留历史约束；涉及学校身份、域名/HTTPS与未实现状态时以本文件和DEC-018及当前实现报告为准。继续使用现有GitHub仓库，通过开发分支/PR上传，不伪造同学个人贡献或老师验收。

