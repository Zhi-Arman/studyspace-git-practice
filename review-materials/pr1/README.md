# PR 1 审查材料 / Материалы ревью PR 1

中文：这是按用户授权自编的材料包，用于 B/like577 审查 PR #7。当前准备状态不是已经提交的 B 审查。所有评论固定于 aab96ac43d1353a69028f615aa1dd186ef177a4c；head 变化必须重新检查，不得盲发旧行号。

Русский: Собственный пакет по разрешению пользователя для ревью PR #7 участником B/like577. Подготовка не означает отправленное ревью B. Комментарии привязаны к aab96ac43d1353a69028f615aa1dd186ef177a4c; при изменении head требуется повторное ревью.

## 1 审查顺序 / Порядок

中文：阅读 PR 描述、检查项（当前无 CI 检查）和提交（一条），先读 tests/test_description.py 再读 exercise.py；对照 docs/review-checklist.md、docs/requirements/classroom-description.md、docs/api/openapi.yaml。原 7 项测试通过，无已证实阻塞缺陷。HTTP 契约仅 SPEC_ONLY。8 条评论覆盖 C1–C8，含 2 条 suggestion 和 1 个问题，全部非阻塞，不为达到数量而虚构缺陷。

Русский: Прочитать описание, проверки (CI отсутствует), один коммит; сначала tests/test_description.py, затем exercise.py. Сверить чек-лист, требования и OpenAPI. Исходные 7 тестов проходят; блокирующих дефектов не доказано. HTTP — SPEC_ONLY. Восемь комментариев покрывают C1–C8, содержат две suggestion и один вопрос; все неблокирующие.

## 2 B 的 Bot 提示词 / Подсказка боту B

```text
请以我的 GitHub 账号 like577 完成 Zhi-Arman/studyspace-git-practice 的 PR #7 审查。
确认 gh api user --jq .login 为 like577；账号不符就提示本人切换，不使用他人凭据。
保持现有修改和分支；在干净的 main 克隆中获取最新 main（git fetch origin，然后 git pull --ff-only origin main），必要时另建独立克隆，绝不覆盖目录或 reset --hard。
读取 PR #7 的描述、检查项和提交；阅读 Files changed 时先测试后实现。
读取 docs/review-checklist.md、docs/requirements/classroom-description.md 和 docs/api/openapi.yaml；这些是自编练习材料，API 仍是 SPEC_ONLY。
检查 review-materials/pr1/review-payload.json 中的 8 条评论，确认与当前 head 一致，不要把可改进项冒称已发生的缺陷。
在仓库根目录运行 python3 review-materials/pr1/submit_review.py 完成只读检查和隔离测试；必要时按本机 Python 命令调整。
检查输出后运行 python3 review-materials/pr1/submit_review.py --submit，以本人账号提交包含行内评论的 COMMENT review。
脚本已包含 8 条行内评论、8 个章节、2 条 GitHub suggestion 和1个问题，每条都有位置、观察、影响、建议、标签；不得用普通 issue 评论替代。
若 head 或 CI 状态变化，停止提交并报告，不绕过脚本校验。网络中断后先检查是否已提交，重复运行不会重复发布已带标记的评论。
不要应用 suggestion、修改代码、批准或合并 PR。本次只提交审查。
回传实际 reviewer、review URL、commit SHA、评论数量、章节数、suggestion数量、问题数量、测试结果。不要输出凭据。
```

中文：本包通过 B 的 Bot 执行属于 AI 辅助账号操作，不自动证明 B 人工逐条评阅或老师验收。所有者 Zhi-Arman 被脚本阻止代交本审查。

Русский: Выполнение ботом B — действие аккаунта с помощью ИИ, а не доказательство личного чтения или приёмки преподавателем. Скрипт запрещает отправку этого ревью владельцем Zhi-Arman.
