# Git 环境与角色练习

Подготовка среды Git и роли

2026-10-21 · v1 · LOCAL_DEMO · 平台选择 GitHub / Выбран GitHub

本地演示已完成，26 项仓库检查通过；线上仓库 NOT_CREATED，两位同学本人执行 NOT_VERIFIED。

Локальное упражнение завершено, пройдены 26 проверок. Онлайн-репозиторий NOT_CREATED, личное выполнение двух студентов NOT_VERIFIED.

## 交付文件 / Материалы

- [中俄双语 Word 报告 / Отчёт Word](Git环境准备与双人角色分工_中俄双语_v1.docx)
- [同内容 Markdown / Тот же текст Markdown](Git环境准备与双人角色分工_中俄双语_v1.md)
- [A 用户指南 / Руководство пользователя A](participant-a/user-guide.md)
- [B 管理员指南 / Руководство администратора B](participant-b/admin-guide.md)
- [本地仓库检查结果 / Результаты проверок](artifacts/execution.json)
- [完整命令记录 / Журнал команд](artifacts/commands.log)

## 打开与复核 / Открытие и проверка

学习根目录 / Корень упражнения:

```text
/Users/zhi/Documents/软件生命周期/studyspace/coursework/2026-10-21-git-environment-roles-v1
```

A 在 VS Code 打开 participant-a，B 打开 participant-b。双方分别在终端切换到自己的文件夹，执行报告第 4 节命令，记录本人姓名、日期与终端结果。当前配置身份为本地演示角色，请用 git config --local 设置本人身份。配置变化只影响后续提交。

A открывает participant-a в VS Code, B — participant-b. Каждый выполняет команды раздела 4 в своём каталоге и записывает имя, дату и результат. Текущие подписи учебные; задайте собственную подпись через git config --local. Это влияет только на будущие коммиты.

当前 origin 指向绝对路径 /Users/zhi/Documents/软件生命周期/studyspace/coursework/2026-10-21-git-environment-roles-v1/teaching-origin.git，只在这台电脑有效。不要把本地裸仓库当成已创建的 GitHub 仓库。若整体移动目录，应在 A/B 各仓库执行 git remote set-url origin 后接新裸仓库路径。

Текущий origin указывает на абсолютный путь локального teaching-origin.git и работает на этом компьютере. Онлайн-репозиторий GitHub ещё не создан. При переносе всей папки обновите origin у A/B командой git remote set-url origin с новым путём к bare-репозиторию.

## 来源与执行 / Источники и выполнение

任务来源为附图“Готовность среды и роли”，含 6 个要点，建议 10 分钟。原图保存在 artifacts/assignment.jpg；Git 版本以当前终端实测为准。指南是本练习的双语文件，未替换既有课程材料。

Источник — фото «Готовность среды и роли»: 6 пунктов, 10 минут. Фото сохранено в artifacts/assignment.jpg; версия Git проверена в терминале. Руководства созданы для этого упражнения и не заменяют прежние материалы.

本机自动执行了 A/B 两种角色的命令，不能替代两名同学本人操作和教师确认。GitHub 建库、真实账号授权、VS Code 预览和应用业务测试本轮未执行。

Команды обеих ролей выполнены автоматически на одном компьютере. Это не заменяет личную работу двух студентов и подтверждение преподавателя. Создание GitHub, права реальных аккаунтов, предпросмотр VS Code и бизнес-тесты не выполнялись.

## 任务二 项目材料组成 / Задача 2 Состав проекта

第二张图的材料整理已放在 [任务二说明](02-project-composition/README.md)。直接使用 [脱敏材料包 README](02-project-composition/project-docs/README.md)，并阅读 [存储策略](02-project-composition/project-docs/STORAGE_POLICY.md)。该材料包保留相对路径，未复制 .git，也未执行 git add。

Материалы второго фото находятся в [описании задачи 2](02-project-composition/README.md). Откройте [README обезличенного комплекта](02-project-composition/project-docs/README.md) и [политику хранения](02-project-composition/project-docs/STORAGE_POLICY.md). Относительные пути сохранены, .git не копировался, git add не выполнялся.
