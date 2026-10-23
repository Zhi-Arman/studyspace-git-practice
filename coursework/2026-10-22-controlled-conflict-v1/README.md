# StudySpace 可控合并冲突

StudySpace Контролируемый конфликт

SS-GIT-CONFLICT-01 · v1.0 · 2026-10-22 · Asia/Shanghai · 文档 DRAFT

SS-GIT-CONFLICT-01 · v1.0 · 22.10.2026 · Asia/Shanghai · Документ DRAFT

可控冲突已真实复现。A、B 从同一提交分支，仅修改同一行；A 已先合并，B 合并到更新后的 main 时发生内容冲突。B 工作区保留未解决状态，任务达到预期终点。

Контролируемый конфликт реально воспроизведён. A и B созданы от одного коммита и изменяют одну строку. A слит первым; слияние B в обновлённую main вызвало конфликт содержимого. Каталог B сохранён в неразрешённом состоянии; цель задания достигнута.

```text
A PR https://github.com/Zhi-Arman/studyspace-git-practice/pull/2
B PR https://github.com/Zhi-Arman/studyspace-git-practice/pull/3
```

| 编号<br>Код | 图片要求<br>Требование на фото | 实际结果<br>Результат |
| --- | --- | --- |
| CF-01 | 创建 docs/build-check.md<br>Создайте учебный файл docs/build-check.md | 已在共同基线提交中创建<br>Создан в общем базовом коммите |
| CF-02 | 添加一行构建检查命令<br>Добавьте одну строку с командой проверки сборки | 文件恰好一行 Sphinx 命令<br>В файле ровно одна команда Sphinx |
| CF-03 | A、B 从同一提交创建独立分支<br>A и B создают отдельные ветки от одного коммита | 共同父提交 569a94a<br>Общий родитель 569a94a |
| CF-04 | 每人只修改这一行<br>Каждый меняет только эту строку | A 加 -W；B 加 -n；各自 1 行替换<br>A добавил -W, B добавил -n; по одной замене |
| CF-05 | A 先合并自己的分支<br>A объединяет свою ветку первым | PR #2 已合并；main 使用 A 命令<br>PR #2 слит; main содержит команду A |
| CF-06 | B 尝试合并并得到冲突<br>B пытается объединить свою ветку и получает конфликт | 退出码 1；UU docs/build-check.md；PR #3 冲突<br>Код 1; UU docs/build-check.md; PR #3 конфликтует |

沿用用户已授权的单账号自动化角色演示：课堂 A 为支浩然，B 为俞智文；实际 GitHub 账号为 Zhi-Arman。真人本人执行与独立批准为 NOT_VERIFIED。

Использована разрешённая пользователем автоматическая демонстрация одним аккаунтом: учебный A 支浩然, B 俞智文; фактический аккаунт GitHub Zhi-Arman. Личное выполнение и независимое одобрение студентов — NOT_VERIFIED.

## 2 同源分支与真实冲突证据

2 Общая база и свидетельства конфликта

先在 docs/conflict-base 创建文件并提交，再分别创建 docs/conflict-a 与 docs/conflict-b。两次修改的父提交和 merge-base 均等于共同基线，排除了分支起点不同造成的干扰。

Сначала файл создан и закоммичен в docs/conflict-base, затем созданы docs/conflict-a и docs/conflict-b. Родитель обоих изменений и merge-base совпадают с общей базой; обе ветки имеют одинаковую исходную версию.

| 版本<br>Версия | 文件中的唯一一行<br>Единственная строка файла |
| --- | --- |
| 基线<br>База | .venv/bin/python -m sphinx -b html docs site |
| A<br>A | .venv/bin/python -m sphinx -W -b html docs site |
| B<br>B | .venv/bin/python -m sphinx -n -b html docs site |

A 合并后，B 先快进同步 main，再执行以下真实命令。退出码为 1，Git 明确报告 docs/build-check.md 的内容冲突。

После слияния A каталог B получил main через fast-forward и выполнил реальную команду ниже. Код возврата 1; Git сообщил о конфликте содержимого docs/build-check.md.

```text
git merge --no-ff --no-edit docs/conflict-b

Auto-merging docs/build-check.md
CONFLICT (content): Merge conflict in docs/build-check.md
Automatic merge failed; fix conflicts and then commit the result.
```

冲突标记由 Git 自动写入，以下为现场文件原文。HEAD 一侧是 main 上的 A 版本，另一侧是 B 分支版本。

Маркеры конфликта записаны Git автоматически. Ниже точное содержимое файла: сторона HEAD — версия A из main, другая сторона — версия ветки B.

```text
<<<<<<< HEAD
.venv/bin/python -m sphinx -W -b html docs site
=======
.venv/bin/python -m sphinx -n -b html docs site
>>>>>>> docs/conflict-b
```

| 索引阶段<br>Стадия | 来源<br>Источник | 已验证内容<br>Проверенное содержание |
| --- | --- | --- |
| 1 | 共同祖先<br>Общая база | 等于基线命令<br>Совпадает с базовой командой |
| 2 | ours 即 main 上的 A<br>ours версия A из main | 等于带 -W 的 A 命令<br>Команда A с -W |
| 3 | theirs 即 B 分支<br>theirs ветка B | 等于带 -n 的 B 命令<br>Команда B с -n |

## 3 验证结果与保留现场

3 Результаты проверки и сохранённое состояние

执行时间 2026-10-22T10:48:33.001519+08:00。准备检查 16/16、最终流程检查 37/37 全部通过。退出码 1 是本题预期的冲突结果。

Время выполнения 2026-10-22T10:48:33.001519+08:00. Пройдены 16/16 подготовительных и 37/37 итоговых проверок. Код 1 — ожидаемый результат конфликта в этом задании.

| 对象<br>Объект | 保留状态<br>Сохранённое состояние |
| --- | --- |
| GitHub main | A 合并提交 ab59f23；未包含 B 的冲突解决<br>Слияние A ab59f23; разрешение конфликта B не добавлено |
| A PR / B PR | A 已合并；B 保持打开，GitHub mergeable=false<br>A слит; B открыт, GitHub mergeable=false |
| A 工作区<br>Каталог A | main 与 GitHub 一致，工作区干净<br>main совпадает с GitHub, дерево чистое |
| B 工作区<br>Каталог B | main 上合并未完成；唯一未合并文件为 docs/build-check.md<br>Незавершённое слияние в main; единственный неслитый файл docs/build-check.md |
| 分支与既有文件<br>Ветки и прежние файлы | 基线、A、B、旧 docs/preview 分支均保留；既有共享文档和 StudySpace 根仓库未改<br>База, A, B и прежняя docs/preview сохранены; прежние документы и корень StudySpace не изменены |

构建命令是本次冲突练习的文本。共享仓库没有完整 Sphinx 配置，构建执行与业务测试均为 NOT_RUN；不能据此声称文档网站构建通过。冲突解决留给后续任务。

Команды сборки используются как текст упражнения. В общем репозитории нет полной конфигурации Sphinx: сборка и бизнес-тесты имеют статус NOT_RUN. Успешная сборка сайта не заявляется; разрешение конфликта оставлено следующему заданию.

交付根目录如下。实际冲突文件位于 author-b/docs/build-check.md；可以查看文件及 git status，继续下一步前应保留当前合并状态。

Ниже корень материалов. Фактический конфликт находится в author-b/docs/build-check.md. Для просмотра откройте файл и git status; до следующего шага сохраняйте текущее состояние слияния.

```text
/Users/zhi/Documents/软件生命周期/studyspace/coursework/2026-10-22-controlled-conflict-v1

README.md
StudySpace_可控合并冲突_中俄双语_v1.docx
author-b/docs/build-check.md
artifacts/task.jpg
artifacts/preparation.json
artifacts/execution.json
artifacts/merge-output.txt
artifacts/status-conflict.txt
artifacts/index-stages.txt
artifacts/conflict-file.txt
artifacts/stage-1.txt  stage-2.txt  stage-3.txt
```

## 文件入口 Входные файлы

[双语 Word Двуязычный Word](StudySpace_可控合并冲突_中俄双语_v1.docx)
[A PR 已合并 A PR слит](https://github.com/Zhi-Arman/studyspace-git-practice/pull/2)
[B PR 冲突 B PR конфликт](https://github.com/Zhi-Arman/studyspace-git-practice/pull/3)
[实际冲突文件 Фактический конфликт](author-b/docs/build-check.md)
[完整流程检查 Проверки](artifacts/execution.json)
