# Git环境准备与双人角色分工

Подготовка среды Git и распределение ролей

版本 1  日期 2026-10-21  文档状态 DRAFT  执行状态 LOCAL_DEMO

Версия 1  Дата 21.10.2026  Документ DRAFT  Выполнение LOCAL_DEMO

独立学习目录和 A/B 两个本地仓库已准备，Git 命令与文件分工检查通过。选定线上平台为 GitHub；当前练习通过本地裸仓库交换提交。

Подготовлены отдельная учебная папка и два локальных репозитория A/B. Проверены команды Git и распределение файлов. Выбрана платформа GitHub; сейчас обмен коммитами идёт через локальный bare-репозиторий.

| 编号<br>Код | 图片要求<br>Требование на фото | 完成情况<br>Результат |
| --- | --- | --- |
| GIT-01 | 打开独立学习文件夹<br>Откройте отдельную учебную папку | PASS<br>已新建本练习目录<br>Создана отдельная папка |
| GIT-02 | 在终端检查 Git<br>Проверьте Git в терминале | PASS<br>Git 2.54.0 可运行<br>Git 2.54.0 работает |
| GIT-03 | 选择 GitHub、GitLab 或教学服务器<br>Выберите GitHub, GitLab или учебный сервер | 已选 GitHub<br>Выбран GitHub<br>线上仓库 NOT_CREATED |
| GIT-04 | A 创建初始仓库，B 随后克隆<br>A создаёт исходный репозиторий; B клонирует его позднее | LOCAL_DEMO PASS<br>A 建库并首次提交后 B 克隆<br>B клонировал после первого коммита A |
| GIT-05 | A 编辑 user-guide.md，B 编辑 admin-guide.md<br>A работает с user-guide.md; B с admin-guide.md | PASS<br>两个角色分别提交指定文件<br>Каждая роль изменила свой файл |
| GIT-06 | 每个人亲自检查命令<br>Проверяйте команды от своего имени, а не только смотрите на партнёра | 本地角色检查 PASS<br>Проверка локальных ролей PASS<br>真人独立操作 NOT_VERIFIED |

图中建议用时 10 分钟。本地演示身份只用于验证流程；双方本人操作与课堂确认由参与者完成。

На фото отведено 10 минут. Учебные подписи используются для проверки процесса; личное выполнение и подтверждение в аудитории выполняют участники.

## 2 目录与角色

2 Папки и роли

本练习位于 StudySpace 的 coursework 下，使用独立 Git 元数据。既有项目文件未改动，原项目仓库未创建提交。

Упражнение находится в coursework проекта StudySpace и имеет отдельные данные Git. В исходном репозитории проекта коммиты не создавались и файлы не изменялись.

```bash
2026-10-21-git-environment-roles-v1/
  participant-a/       # A 的工作区 / каталог A
    user-guide.md
    admin-guide.md
  participant-b/       # B 的克隆 / клон B
    user-guide.md
    admin-guide.md
  teaching-origin.git/ # 本地裸仓库 / локальный bare
  artifacts/           # 命令记录 / журналы
  README.md
```

A 负责创建初始仓库和 user-guide.md；B 克隆后负责 admin-guide.md。两份文件都存在于两个工作区中，分工通过各自的后续提交体现。

A создаёт исходный репозиторий и ведёт user-guide.md. B клонирует его и ведёт admin-guide.md. Оба файла есть в обоих рабочих каталогах; распределение подтверждено отдельными последующими коммитами.

本地身份分别为 Participant A (local exercise) 和 Participant B (local exercise)，邮箱使用 example.invalid。配置仅写入练习仓库，真实参与者应设置自己的本地提交身份。

Локальные подписи: Participant A (local exercise) и Participant B (local exercise), адреса в example.invalid. Настройки записаны только в учебные репозитории. Участники задают собственные локальные подписи.

A 负责用户指南中的编辑、保存和预览步骤；B 负责仓库准备、同步与常见问题。每个人先确认当前目录与身份，再检查自己负责的文件差异。

A описывает редактирование, сохранение и предпросмотр. B описывает подготовку репозитория, синхронизацию и частые затруднения. Каждый сначала проверяет каталог и подпись, затем diff своего файла.

本轮属于 Git 文档协作练习。StudySpace 原有业务状态与团队长期角色不因本练习改变。

Это упражнение по совместной работе с документацией в Git. Оно не изменяет состояние бизнес-функций StudySpace и постоянные роли команды.

选定 GitHub 尚需线上建库与访问权限设置；本地 origin 只接受本机练习提交。VS Code 预览、真人双账号权限和应用业务测试本轮未验证。

Для выбранного GitHub ещё требуются создание онлайн-репозитория и права доступа. Локальный origin обслуживает только упражнение на этом компьютере. Предпросмотр VS Code, права двух реальных аккаунтов и бизнес-тесты приложения сейчас не проверялись.

## 3 已执行的协作流程

3 Выполненный порядок работы

执行顺序为 A 首次提交、B 克隆、A 修改用户指南、B 同步并修改管理员指南、A 再同步。以下列出实际操作摘要；完整参数与退出码保存在 artifacts/commands.log。

Порядок: первый коммит A, клонирование B, правка руководства пользователя A, получение B и правка руководства администратора, затем получение A. Ниже основные команды; полные параметры и коды выхода в artifacts/commands.log.

准备阶段先创建 teaching-origin.git 裸仓库，再初始化 participant-a 的 main 分支。A 首次提交包含 README.md、两份指南和 .gitignore，随后推送到本地 origin。

Сначала создан bare-репозиторий teaching-origin.git и ветка main в participant-a. Первый коммит A содержит README.md, два руководства и .gitignore, затем отправлен в локальный origin.

```bash
git init --bare --initial-branch=main teaching-origin.git
git init --initial-branch=main participant-a
# 在 A 工作区内 / В рабочем каталоге A
git add README.md user-guide.md admin-guide.md .gitignore
git commit -m "docs: initialize bilingual guide practice"
git remote add origin ../teaching-origin.git
git push -u origin main
# 回到练习根目录后 / Из корня упражнения
git clone --no-hardlinks teaching-origin.git participant-b
```

首次初始化和克隆已完成，请在新空白目录中复现这些步骤。为保持本地路径明确，实际记录中的 origin 与 clone 参数使用绝对路径。

Инициализация и клонирование уже выполнены; воспроизводите их в новой пустой папке. В журнале для origin и clone использованы абсолютные пути.

```bash
# A 保存 user-guide.md 后 / A сохраняет user-guide.md
git add user-guide.md
git commit -m "docs: add user guide editing steps"
git push origin main
# B 先同步再保存 admin-guide.md / B получает A и правит файл
git pull --ff-only origin main
git add admin-guide.md
git commit -m "docs: add admin guide repository checks"
git push origin main
# A 最后同步 / A получает итоговый коммит B
git pull --ff-only origin main
```

## 4 检查结果与个人复核

4 Результаты и личная проверка

执行日期 2026-10-21，终端返回 git version 2.54.0 (Apple Git-157)。本轮 26 项本地仓库检查全部通过；两个工作区各有 3 个提交，最终提交一致。

Дата выполнения 21.10.2026; терминал: git version 2.54.0 (Apple Git-157). Пройдены все 26 проверок локальных репозиториев. В каждом рабочем каталоге 3 коммита; итоговый коммит совпадает.

| 检查项<br>Проверка | 实际结果<br>Фактический результат |
| --- | --- |
| 仓库独立性<br>Изоляция репозиториев | A/B 各有独立 Git 根目录<br>У A/B отдельные корни Git |
| 克隆顺序<br>Порядок клонирования | B 克隆时 HEAD 等于 A 的初始提交<br>HEAD B при клонировании равен первому коммиту A |
| 指定文件分工<br>Распределение файлов | A 后续提交仅 user-guide.md；B 仅 admin-guide.md<br>A изменил только user-guide.md, B только admin-guide.md |
| 同步与完整性<br>Синхронизация и целостность | A、B、origin 的 main 一致；fsck 通过<br>main A, B и origin совпадает; fsck пройден |
| 工作区<br>Рабочее дерево | A/B 的 status --porcelain 均无输出<br>status --porcelain у A/B пуст |
| 线上与本人操作<br>Онлайн и личное выполнение | GitHub NOT_CREATED；真人 NOT_VERIFIED<br>GitHub NOT_CREATED; личное выполнение NOT_VERIFIED |

双方分别在自己的工作区执行以下命令。检查仓库根目录与身份，确认 main 分支、两份指南和提交记录；完成同步后工作区应干净。

Каждый выполняет команды в своём рабочем каталоге. Проверьте корень, подпись, ветку main, два руководства и историю. После синхронизации рабочее дерево должно быть чистым.

```bash
pwd
git --version
git rev-parse --show-toplevel
git config --local --get user.name
git config --local --get user.email
git branch --show-current
git status --short
git log --oneline -3
git rev-parse HEAD
```

本轮最终提交前 12 位为 56dd40ab7e85。A、B 分别自行复核并记录姓名、日期与输出后，才能确认“本人独立执行”。

Первые 12 символов итогового коммита: 56dd40ab7e85. Для подтверждения личного выполнения A и B самостоятельно проверяют команды и записывают имя, дату и вывод.
