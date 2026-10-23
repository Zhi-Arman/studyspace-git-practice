# 曹浩然个人贡献记录 / Личный вклад Цао Хаожань

## 中文

### 基本信息
- **姓名**：曹浩然
- **本次协作角色**：成员 B
- **GitHub 用户名**：like577
- **学号**：202311611H101
- **日期**：2026-10-23（Asia/Shanghai）
- **操作系统**：Linux x86_64（Grok Bot 工作机；本人 Windows 本机 PATH 未配置 `gh`，Python Store 入口不可用，故在已登录 like577 的同一协作环境完成克隆、测试与推送）
- **Python 版本**：Python 3.13.5（`python3`）
- **测试基准提交 SHA**：`d4b48a298a87b3a145363e23530bc1c5ea2d760b`（`origin/main`，消息：`docs: finalize public course-v1 submission package`）
- **个人分支**：`docs/caohaoran-test-evidence`
- **辅助说明**：本记录与提交流程由 Grok Bot（小支浩然）按本人指令辅助完成；**不把仓库中已有业务代码或 classroom-git 功能实现声称为本人编写**；不编造未运行的测试结果，不声称老师已验收。

### 本人实际阅读与核查
1. `README.md`：Docker / 原生启动、检查命令、本地账号与范围说明。
2. `REPORT.md`：交付范围、角色表、测试边界与 NOT_RUN 原则。
3. `CONTRIBUTING.md`：本人账号贡献步骤与贡献记录最小格式。
4. `classroom-git/README.md`：双人 PR 练习范围、A/B 分支约定、运行方式；确认 main 上仅为公共基础，A/B 功能在各自 feature 分支。
5. 顺带核对：`scripts/check.sh` 依赖 `backend/.venv`（需先 `bash scripts/setup.sh`）；当前环境无该虚拟环境，也无 Docker。

### 实际运行的命令与真实结果

#### 1）课堂基础单元测试（已运行）
工作目录：`classroom-git`

```text
python3 -m unittest discover -s tests -v
```

真实输出摘要：

```text
test_default_status (test_ticket.TicketTests.test_default_status) ... ok
test_description_preserved (test_ticket.TicketTests.test_description_preserved) ... ok
----------------------------------------------------------------------
Ran 2 tests in 0.000s
OK
```

结论：main 上 classroom-git 基础 Ticket 测试 **2/2 通过**。  
覆盖范围仅限当前 main 公共基础（默认状态 `new`、描述保留），**不代表**：
- 完整 StudySpace 网站业务已验证；
- `feature/description-validator`（A）或 `feature/status-transitions`（B）功能已在本分支验证；
- 老师正式验收已完成。

#### 2）根目录完整检查（NOT_RUN）
```text
bash scripts/check.sh
```

真实结果：脚本立即退出并打印 `Run bash scripts/setup.sh first.`  
原因：`backend/.venv/bin/python` 不存在；本环境未预先配置网站运行依赖，也未安装/启动 Docker。按要求**未擅自执行完整 setup 后冒充“网站检查已通过”**，记为 **NOT_RUN**。

### 发现的问题 / 限制
1. 本人 Windows 电脑（Novoamor）当前会话中 `git`/`gh` 不在 PATH，Store 版 `python` 不可用；实际 GitHub 操作用登录为 like577 的协作 Linux 环境完成。
2. `scripts/check.sh` 在未 setup 时无法运行；未配置网站环境前不应引用他人历史成功结果。
3. classroom-git main 测试集很小（2 项），不能外推为全站或未合并 feature 已验证。
4. 本 PR 仅新增本人贡献文档，不合并、不自批、不移动 `course-v1.0` 标签。

### 提交后回填
- **本人 commit SHA**：提交后回填
- **PR 链接**：提交后回填
- **PR 创建者**：like577（预期）

---

## Русский

### Основные сведения
- **ФИО**: Цао Хаожань (曹浩然)
- **Роль в этом задании**: участник B
- **GitHub**: like577
- **Дата**: 2026-10-23 (Asia/Shanghai)
- **ОС**: Linux x86_64 (рабочая машина Grok Bot; на Windows PATH без `gh`, Store Python недоступен)
- **Python**: 3.13.5
- **Базовый SHA**: `d4b48a298a87b3a145363e23530bc1c5ea2d760b` (`origin/main`)
- **Ветка**: `docs/caohaoran-test-evidence`
- **Помощь**: процесс выполнен с помощью Grok Bot по моей инструкции; **существующий код не заявлен как написанный мной**; результаты не выдуманы; приёмка преподавателя не утверждается.

### Что реально прочитано
`README.md`, `REPORT.md`, `CONTRIBUTING.md`, `classroom-git/README.md`; проверено, что `scripts/check.sh` требует `backend/.venv`.

### Команды и результаты
1. В `classroom-git`: `python3 -m unittest discover -s tests -v` → **2 теста OK** (только база main).
2. `bash scripts/check.sh` → **NOT_RUN** (`Run bash scripts/setup.sh first.`; нет venv/Docker, полный setup не запускался для имитации успеха).

### Ограничения
Базовые тесты classroom-git ≠ проверка всего сайта и feature-веток. Этот PR только добавляет документ вклада; без merge/self-approve и без изменения тега `course-v1.0`.

### После публикации
- SHA коммита и ссылка PR будут заполнены после push/create.
