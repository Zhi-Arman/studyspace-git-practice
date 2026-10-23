"""Migrate existing learning documents without modifying their sources."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
PACK = ROOT.parent.parent
DOCS = ROOT / 'docs'
ART = ROOT / 'artifacts'
for directory in [DOCS / 'images', DOCS / '_static', DOCS / 'materials', ART]:
    directory.mkdir(parents=True, exist_ok=True)

def write(path, text):
    (ROOT / path).write_text(text.strip() + '\n', encoding='utf-8')

old = json.loads((PACK / '07-admin-guide/data/content.json').read_text())
manifest = []
def retain(relative):
    src = PACK / relative
    dst = DOCS / 'materials' / relative
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    assert digest == hashlib.sha256(dst.read_bytes()).hexdigest()
    manifest.append({'source': str(src), 'copy': str(dst.relative_to(ROOT)), 'sha256': digest})

paths = {row[2] for row in old['references']}
paths.update(['admin-guide.md', 'StudySpace_管理员指南_中俄双语_v1.docx',
              '05-guide-3.4.3/candidates/user-guide.md', '05-guide-3.4.3/remarks-register.md',
              'artifacts/guide-3.4.3-confirmation.json', '07-admin-guide/data/content.json'])
for adr in ['0001-simple-monolith.md', '0002-sqlite-postgresql.md', '0004-docker-https.md']:
    paths.add('00-project/docs/decisions/ru-RU/' + adr)
for path in sorted(paths):
    retain(path)

chapters = {}
for b in old['blocks']:
    if b['type'] == 'heading' and b['level'] == 2:
        chapter = int(b['zh'].split()[0])
        chapters[chapter] = []
    chapters[chapter].append(dict(b))

blocks = []
def pair(zh, ru):
    return {'type': 'pair', 'zh': zh, 'ru': ru}
def heading(level, zh, ru):
    return {'type': 'heading', 'level': level, 'zh': zh, 'ru': ru}

titles = {
  1: ('1 用途与组成', '1 Назначение и состав'),
  2: ('2 要求与访问', '2 Требования и доступ'),
  3: ('3 安装与验证', '3 Установка и проверка'),
  4: ('4 配置', '4 Конфигурация'),
  5: ('5 启动停止与观察', '5 Запуск остановка и наблюдение'),
  6: ('6 备份与恢复', '6 Резервное копирование и восстановление'),
  7: ('7 更新与回滚', '7 Обновление и откат'),
  8: ('8 诊断', '8 Диагностика'),
  9: ('9 限制与未验证说明', '9 Ограничения и непроверенные инструкции')}

purposes = {
 'AG-P01': ('在学习副本中重现锁定的应用依赖。', 'Воспроизвести зависимости учебной копии по lock-файлам.'),
 'AG-P02': ('在回环地址启动并正常停止学习服务。', 'Запустить учебные сервисы на loopback и штатно остановить их.'),
 'AG-P03': ('用可观察结果区分进程存活、数据库连通和代理状态。', 'Различить доступность процесса, соединение БД и прокси по наблюдаемым результатам.'),
 'AG-P04': ('将合成 SQLite 数据备份并恢复到全新候选文件。', 'Создать копию синтетической SQLite и восстановить в новый файл.')}
verified = {
 'AG-P01': ('部分验证。执行者为 Codex，2026-10-21，macOS arm64、Python 3.13.12、学习包根 .venv；后端安装引用 R10。完整前端安装未验证。', 'Частично проверено. Codex, 21.10.2026, macOS arm64, Python 3.13.12, корневая .venv; установка сервера по R10. Полная установка клиента не проверена.'),
 'AG-P02': ('未验证。当前仅审阅命令与源文件；本轮未启动 StudySpace 服务，执行人、运行日期和运行环境尚无实测记录。', 'Не проверено. Просмотрены команды и исходники; сервисы StudySpace сейчас не запускались, нет фактической записи исполнителя, даты и среды запуска.'),
 'AG-P03': ('部分验证。Codex，2026-10-21，学习副本、Python 3.13.12、进程内 TestClient；引用 R11 的 8 passed、1 warning。真实服务 HTTP、Vite 代理与业务验收未验证。', 'Частично проверено. Codex, 21.10.2026, учебная копия, Python 3.13.12, TestClient; R11: 8 passed, 1 warning. HTTP сервисов, Vite и бизнес-приёмка не проверены.'),
 'AG-P04': ('仅合成演练通过。Codex，2026-10-21，macOS、Python 3.13.12、SQLite，两条合成记录；引用 R12。未激活候选，真实业务恢复未验证。', 'Проверено только синтетическое упражнение. Codex, 21.10.2026, macOS, Python 3.13.12, SQLite, две записи; R12. Кандидат не активирован, бизнес-восстановление не проверено.')}

procedure_schema = ['用途 / Назначение', '前置条件 / Предусловия', '操作 / Действия',
                    '预期结果 / Ожидаемый результат', '失败处理 / При неуспехе', '验证记录 / Проверено']

def use_chapter(old_num, new_num, procedure=None):
    seq = [dict(b) for b in chapters[old_num]]
    seq[0].update(zh=titles[new_num][0], ru=titles[new_num][1])
    for b in seq[1:]:
        if b['type'] == 'heading':
            for lang in ['zh', 'ru']:
                b[lang] = re.sub(r'^' + str(old_num) + r'\.', str(new_num) + '.', b[lang])
        for lang in ['zh', 'ru', 'text']:
            if lang in b:
                b[lang] = b[lang].replace('随后执行第 6 章检查', '随后执行本章 AG-P03 检查')
                b[lang] = b[lang].replace('и выполнить главу 6', 'и выполнить AG-P03 этой главы')
                b[lang] = b[lang].replace('本次恢复演练', '前阶段恢复演练')
                b[lang] = b[lang].replace('Текущее упражнение', 'Прежнее упражнение')
    if old_num == 2:
        for b in seq:
            if b['type'] == 'code':
                b['text'] = 'cd ../..\n# 从 project-docs 到学习包根目录 / Из project-docs в корень учебного пакета'
        seq.insert(1, pair('应用操作均从父学习包根目录执行；文档站构建则从 project-docs 根目录执行。两处 .venv 用途不同，不要混用。', 'Операции приложения выполняются из корня учебного пакета, сборка сайта из project-docs. Две .venv имеют разное назначение.'))
    if procedure:
        seq.insert(1, heading(3, procedure + ' 流程卡', procedure + ' Карточка процедуры'))
        seq.insert(2, pair('用途：' + purposes[procedure][0], 'Назначение: ' + purposes[procedure][1]))
        seq.append(pair('验证记录：' + verified[procedure][0], 'Проверено: ' + verified[procedure][1]))
    if old_num == 3:
        i = next(i for i,b in enumerate(seq) if b['type'] == 'code')
        seq.insert(i, pair('警告：npm ci 会重建学习副本的 node_modules，uv sync 会同步选定环境。先确认当前路径与锁文件，保留已有配置；不在生产目录执行。步骤为 1 检查版本，2 同步后端，3 安装前端，4 仅缺失时复制示例，5 检查依赖。', 'Предупреждение: npm ci пересоздаёт node_modules, uv sync синхронизирует выбранную среду. Проверить путь и lock-файлы, сохранить настройки; не выполнять в продакшене. Шаги: 1 версии, 2 сервер, 3 клиент, 4 пример только при отсутствии, 5 совместимость.'))
    if old_num == 5:
        i = next(i for i,b in enumerate(seq) if b['type'] == 'code')
        seq.insert(i, pair('编号步骤：1 在终端 A 启动后端；2 在终端 B 启动前端；3 执行 AG-P03；4 在各自终端按 Ctrl+C；5 用 lsof 检查自己的进程已停止。终端输出用于观察，请只保存脱敏片段。', 'Шаги: 1 запустить сервер в A; 2 клиент в B; 3 выполнить AG-P03; 4 Ctrl+C в обоих терминалах; 5 проверить lsof, что свои процессы остановлены. Для наблюдения использовать вывод терминалов, сохранять только безопасные фрагменты.'))
    if old_num == 8:
        i = next(i for i,b in enumerate(seq) if b['type'] == 'code')
        seq.insert(i, pair('警告：禁止覆盖运行中的工作数据库。先停写并保存原配置；本例只恢复到新文件，禁止以原库作为输出。编号步骤：1 核对已停写的合成源库；2 选两个新名称；3 运行命令；4 核对完整性和两条记录；5 保留候选且不激活。', 'Предупреждение: запрещено восстанавливать поверх рабочей БД. Остановить запись, сохранить настройки; вывод только в новые файлы. Шаги: 1 проверить остановленный синтетический источник; 2 выбрать два новых имени; 3 выполнить команду; 4 сверить целостность и две записи; 5 сохранить кандидата без активации.'))
    blocks.extend(seq)

use_chapter(1, 1)
blocks += [pair('下图仅表示已存在的开发链路；生产 Caddy、PostgreSQL 和真实校内核验不在已验证范围。', 'Схема показывает существующую цепочку разработки; Caddy, PostgreSQL и реальная проверка вуза вне проверенной области.'), {'type':'image','path':'images/development-chain.svg'}]
use_chapter(2, 2)
use_chapter(3, 3, 'AG-P01')
use_chapter(4, 4)
use_chapter(5, 5, 'AG-P02')
monitor = [dict(b) for b in chapters[6][1:]]
blocks += [heading(3, '5.5 AG-P03 运行检查流程卡', '5.5 AG-P03 Проверка работоспособности'), pair('用途：' + purposes['AG-P03'][0], 'Назначение: ' + purposes['AG-P03'][1])]
for b in monitor:
    if b['type'] == 'heading':
        b['level'] = 4
        for lang in ['zh','ru']: b[lang] = b[lang].replace('6.', '5.5.')
    if b['type']=='code':
        counter=0
        lines=[]
        for line in b['text'].splitlines():
            if line.startswith('curl '):
                counter+=1
                line += '  # '+str(counter)
            lines.append(line)
        b['text']='\n'.join(lines).replace('# Isolated alternative', '# 5 Isolated alternative')
    if b['type']=='pair' and b['zh'].startswith('浏览器打开'):
        b['zh']='6 '+b['zh']
        b['ru']='6 '+b['ru']
blocks += monitor + [pair('验证记录：' + verified['AG-P03'][0], 'Проверено: ' + verified['AG-P03'][1])]
use_chapter(8, 6, 'AG-P04')
blocks += [heading(2, *titles[7]), heading(3,'AG-P05 更新与回滚流程卡','AG-P05 Карточка обновления и отката'),
 pair('用途：在应用版本更新前验证备份，并在失败时有序回到兼容版本。本节是待执行设计，当前未发布应用新版本。', 'Назначение: проверить резервную копию перед обновлением и вернуться к совместимой версии при сбое. Это план, новый релиз приложения сейчас не выпущен.'),
 heading(3,'7.1 前置条件','7.1 Предусловия'),
 pair('限独立学习副本。需要旧版和候选版制品、两版锁文件、旧配置的受限副本、停写窗口、可读备份及恢复到新文件后的完整性和内容核对记录。缺少任一项则停止更新。当前无 Alembic 迁移或向下迁移脚本，PostgreSQL 路径仍未实现。', 'Только отдельная учебная копия. Нужны старый и новый артефакты, lock-файлы обеих версий, защищённая копия настроек, окно без записи, читаемая резервная копия и проверка целостности/содержимого после восстановления в новый файл. Если чего-либо нет, остановиться. Alembic и downgrade отсутствуют, PostgreSQL не реализован.'),
 heading(3,'7.2 操作','7.2 Действия'),
 pair('警告：更新可能改变依赖或数据模式。更新前先备份，并通过恢复到新文件验证备份可用性。回滚应用不会自动回滚数据库模式；没有已验证的模式兼容或迁移方案时，不进行数据库变更。', 'Предупреждение: обновление может изменить зависимости и схему. До него создать копию и проверить её восстановлением в новый файл. Откат приложения не откатывает схему БД; без проверенной совместимости или миграции схему не менять.'),
 pair('1 记录旧版制品标识、锁文件与配置位置。2 执行 AG-P04 并核对数据，备份不合格即停止。3 将候选版展开至新的学习目录，保留旧目录。4 按 AG-P01 安装候选锁定依赖，明确数据库目标。5 按 AG-P02 和 AG-P03 验证候选；仅在满足既定验收条件后才切换学习入口。6 失败时停止候选，保留日志，恢复旧配置和旧版制品。7 若模式不兼容，停止回滚，不将旧版连接到新模式；在隔离副本恢复已验证的旧数据后再复核。', '1 Записать идентификатор старого артефакта, lock-файлы и настройки. 2 Выполнить AG-P04 и сверить данные; при плохой копии остановиться. 3 Распаковать кандидата в новую учебную папку, сохранив старую. 4 Установить его зависимости по AG-P01 и определить БД. 5 Проверить AG-P02/AG-P03, переключать учебный вход только после критериев приёмки. 6 При сбое остановить кандидата, сохранить журнал, вернуть старые настройки и артефакт. 7 При несовместимой схеме остановить откат, не подключать старый код к новой схеме; восстановить проверенные старые данные в изолированной копии и повторить проверки.'),
 heading(3,'7.3 预期结果','7.3 Ожидаемый результат'),
 pair('候选或回退版本的实际标识与记录一致，锁文件一致，health 和 ready 符合 AG-P03；数据核对有记录，原库与旧制品保留。只有这些现象被实际观察并签录，才能将相应流程改为已验证。', 'Идентификатор кандидата или возвращённой версии совпадает с записью, lock-файлы совпадают, health/ready соответствуют AG-P03; данные сверены, исходная БД и артефакт сохранены. Статус меняется только по фактическому наблюдению и записи.'),
 heading(3,'7.4 失败处理','7.4 При неуспехе'),
 pair('日志先看候选安装输出及前后端终端；不要记录凭据。保留旧目录、备份和失败候选，回到失败的原步骤复核。数据库兼容性未知时保持服务停止，补齐迁移与恢复验证后再继续。', 'Сначала проверить вывод установки и терминалы клиента/сервера, без секретов. Сохранить старую папку, копии и кандидата, повторить исходную проверку. При неизвестной совместимости БД оставить сервис остановленным до проверки миграции и восстановления.'),
 pair('验证记录：未验证 / NOT_RUN。Codex 于 2026-10-21 仅完成文字及源文件一致性审阅；无新版制品、更新执行或回滚运行记录。不得将本地文档站更新当作应用升级验证。', 'Проверено: не проверено / NOT_RUN. Codex 21.10.2026 выполнил только проверку текста и исходников; нет новых артефактов, запуска обновления и отката. Обновление документации не считается проверкой обновления приложения.')]
use_chapter(7, 8)
use_chapter(9, 9)
blocks += [pair('本轮新增实测只涉及 Sphinx 文档站的安装、严格构建和页面检查，记录于 build-evidence.md。原 R10、R11、R12 是前阶段证据引用，并非本轮重新执行。OPEN-008 的课程具体条件同样保持 PARTIAL。未发布网站或内部配置到互联网，未操作生产服务器。', 'Новые проверки касаются только установки Sphinx, строгой сборки и сайта, см. build-evidence.md. R10/R11/R12 цитируются из прежнего этапа и сейчас не повторялись. OPEN-008 также PARTIAL. Сайт и внутренние настройки не публиковались в интернете, продакшен не использовался.'),
 heading(2,'变更历史','История изменений'),
 {'type':'table','headers':['版本 / Версия','日期 / Дата','变更 / Изменение','状态 / Статус'], 'widths':[1.5,2.5,10.4,2.8], 'rows':[
 ['0.1','2026-10-21','原稿八章加限制和历史\n8 глав плюс ограничения и история','DRAFT'],
 ['0.2','2026-10-21','按新图对齐九章模板，补六字段流程卡、更新回滚和 Sphinx\n9 глав по фото, шесть полей, обновление/откат, Sphinx','DRAFT / PARTIAL_VERIFIED']]},
 heading(3,'依据与证据索引','Источники и свидетельства')]
for b in chapters[10]:
    if b['type']=='reference':
        ref=dict(b)
        ref['label']=ref['label'].replace('本次恢复演练','前阶段恢复演练').replace('Текущее упражнение','Прежнее упражнение')
        blocks.append(ref)
blocks += [pair('所有 R01 至 R13 链接指向随站保存的原材料；目录层级保持不变，下载副本 SHA-256 与源文件一致。仅复制公开示例配置和选定源文件，没有复制 .env、真实密钥或学生数据。', 'R01–R13 ведут к сохранённым материалам. Иерархия сохранена, SHA-256 совпадает с исходниками. Скопированы только примеры настроек и выбранные исходники, без .env, секретов и данных студентов.')]

md = ['# StudySpace 管理员手册\n\nРуководство администратора StudySpace\n',
      'SS-DAC-ADMIN-01 · v0.2 · DRAFT · 2026-10-21 · Asia/Shanghai\n',
      '文档版本 0.2；系统版本 0.1.0；需求版本 0.3.0；说明状态为部分验证，各流程单独标注。\n\nВерсия документа 0.2; системы 0.1.0; требований 0.3.0. Инструкции проверены частично, статус указан у каждой процедуры.\n']
for b in blocks:
    t=b['type']
    if t=='heading': md.append('#'*b['level']+' '+b['zh']+' / '+b['ru']+'\n')
    elif t=='pair': md.append(b['zh']+'\n\n'+b['ru']+'\n')
    elif t=='code': md.append('```'+('ini' if b['lang']=='dotenv' else b['lang'])+'\n'+b['text']+'\n```\n')
    elif t=='image': md.append('![开发链路 / Цепочка разработки]('+b['path']+')\n')
    elif t=='reference': md.append('- {download}`'+b['id']+' '+b['label']+' <materials/'+b['path']+'>`')
    elif t=='table':
        md.append('| '+' | '.join(b['headers'])+' |\n| '+' | '.join('---' for _ in b['headers'])+' |')
        md += ['| '+' | '.join(x.replace('|','\\|').replace('\n','<br>') for x in row)+' |' for row in b['rows']]
        md.append('')
write('docs/admin-guide.md','\n'.join(md))
write('artifacts/admin-content.json',json.dumps({'version':'0.2','blocks':blocks,'procedure_schema':procedure_schema},ensure_ascii=False,indent=2))
write('artifacts/source-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))

write('docs/conf.py', '''project = "StudySpace"
author = "StudySpace 课程小组"
copyright = "2026 StudySpace"
release = "0.2"
version = "0.2"
extensions = ["myst_parser"]
source_suffix = {".md": "markdown"}
root_doc = "index"
language = "zh_CN"
exclude_patterns = ["materials/**"]
html_theme = "alabaster"
html_static_path = ["_static"]
html_css_files = ["coursework.css"]
html_title = "StudySpace 中俄双语文档"
html_short_title = "StudySpace"
html_theme_options = {"description": "Docs as code · 3.4.4 · DRAFT", "fixed_sidebar": True}
html_sidebars = {"**": ["about.html", "navigation.html", "searchbox.html"]}
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 4
nitpicky = True
''')
write('docs/_static/coursework.css', '''body { font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Arial", sans-serif; }
div.body { max-width: 1100px; }
div.document { width: min(1360px, 96vw); }
div.body h1, div.body h2, div.body h3 { font-family: inherit; line-height: 1.4; color: #172a3a; }
div.body p, div.body li { line-height: 1.75; }
div.body h2 { border-top: 1px solid #d9e1e7; padding-top: 1.2em; }
table.docutils { width: 100%; font-size: .88em; }
table.docutils td, table.docutils th { padding: .65em; vertical-align: top; overflow-wrap: anywhere; }
table.docutils th { background: #e8f0f4; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; }
img { max-width: 100%; height: auto; }
@media (max-width: 875px) { div.document { width: 100%; } div.bodywrapper { margin: 0; } }
''')
write('docs/images/development-chain.svg','''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="160" viewBox="0 0 1000 160" role="img" aria-label="React to Vite proxy to FastAPI to SQLite">
<rect width="1000" height="160" fill="#f5f8fa"/>
<g fill="#e6eef3" stroke="#628399"><rect x="15" y="30" width="200" height="90" rx="8"/><rect x="270" y="30" width="200" height="90" rx="8"/><rect x="525" y="30" width="200" height="90" rx="8"/><rect x="780" y="30" width="200" height="90" rx="8"/></g>
<g font-family="Arial,sans-serif" font-size="20" fill="#172a3a" text-anchor="middle"><text x="115" y="70">React</text><text x="115" y="98">Browser</text><text x="370" y="70">Vite /api</text><text x="370" y="98">127.0.0.1:5173</text><text x="625" y="70">FastAPI</text><text x="625" y="98">127.0.0.1:8000</text><text x="880" y="70">SQLAlchemy</text><text x="880" y="98">SQLite</text></g>
<g stroke="#52778c" stroke-width="3" fill="none"><path d="M220 75h40m-10-7 10 7-10 7M475 75h40m-10-7 10 7-10 7M730 75h40m-10-7 10 7-10 7"/></g></svg>''')
write('docs/index.md', '''# StudySpace 文档站

Документация StudySpace

文档包 v0.2 · 系统 v0.1.0 · 需求 v0.3.0 · DRAFT · 2026-10-21

这是实践 3.4.4 的本地中俄双语文档站，面向课程成员。先阅读用户指南学习 Markdown，再按管理员手册查看安装、配置、启停、备份、更新与诊断。用户指南沿用用户确认的 3.4.3 材料，主题为 VS Code 文档编辑。

Локальный двуязычный сайт практики 3.4.4 для учебной группы. Руководство пользователя объясняет Markdown, администратора — установку, настройку, запуск, копирование, обновление и диагностику. Пользовательское руководство сохраняет подтверждённую тему 3.4.3 о редактировании документов в VS Code.

:::{important}
应用仍是骨架；38 条需求 PROPOSED，38 个业务用例 NOT_RUN。文档网站检查不等于应用业务验收。\n
Приложение остаётся каркасом; 38 требований PROPOSED, 38 бизнес-кейсов NOT_RUN. Проверка сайта не означает бизнес-приёмку.
:::

```{toctree}
:maxdepth: 2
:caption: 文档目录 Документы

user-guide
admin-guide
release-notes
document-register
```

## 如何阅读 Как читать

每一操作流程均列出用途、前置条件、操作、可观察预期、失败处理及验证记录。未执行步骤明确写“未验证”，不可按文档中的预期结果推断已运行。

Каждая процедура содержит назначение, предусловия, действия, наблюдаемый результат, обработку сбоя и запись проверки. Невыполненные действия отмечены как непроверенные; ожидание не является фактом.

完整构建日志与评审在 project-docs 根目录的 build-evidence.md 和 review.md；文档登记页提供随站下载副本。

Полные журналы и проверка находятся в build-evidence.md и review.md корня project-docs; скачиваемые копии доступны в реестре.
''')
user = (PACK / '05-guide-3.4.3/candidates/user-guide.md').read_text()
user = user.replace('Руководство по Markdown в VS Code для начинающих', '''Руководство по Markdown в VS Code для начинающих

SS-DAC-USER-01 · 原内容 3.4.3 / Исходный материал 3.4.3 · 网站副本 v0.2 · 2026-10-21

用户已确认本材料对应实践 3.4.3。迁移时保留任务 A 与 B 的原有步骤及链接；本轮仅验证网站呈现，未重新执行 VS Code 操作。原文件副本保存在 materials 中。

Пользователь подтвердил соответствие практике 3.4.3. Шаги A и B и ссылки сохранены. Сейчас проверено отображение сайта, действия VS Code не повторялись; исходник сохранён в materials.''',1)
write('docs/user-guide.md',user)
write('docs/release-notes.md', '''# 文档发布说明

Примечания к выпуску документации

SS-DAC-REL-01 · v0.2 · DRAFT · 2026-10-21

## 0.2 文档站初版 Первый сайт документации

本次交付只发布到本地文件夹。新增 Sphinx 与 MyST 配置、四页目录、独立虚拟环境依赖锁、严格构建脚本与验证记录。管理员手册按九章模板整理，新增更新与回滚，四个既有流程及一个计划流程均补齐六字段。3.4.3 用户指南保留其 VS Code 主题及步骤，既有源文件不改。

Результат находится только в локальной папке. Добавлены Sphinx/MyST, четыре страницы, lock-файл отдельной среды, строгая сборка и свидетельства. Руководство администратора приведено к девяти главам с обновлением и откатом; пять процедур имеют шесть полей. Тема VS Code и шаги 3.4.3 сохранены, исходники не изменены.

## 兼容性与迁移 Совместимость и перенос

文档版本由 0.1 升为 0.2；应用仍 0.1.0，需求仍 0.3.0。已有指南及其证据按原目录层级保存在 materials，通过 Sphinx 下载角色链接；清单记录逐文件 SHA-256。没有应用数据库迁移，也没有把应用回退等同数据库模式回退。

Версия документа 0.1 → 0.2; приложение остаётся 0.1.0, требования 0.3.0. Материалы и свидетельства сохранены в materials с исходной иерархией и ссылками скачивания; SHA-256 записан для каждого файла. Миграции БД нет, откат приложения не приравнен к откату схемы.

## 已知限制 Известные ограничения

教师原始起始包和原始意见清单未提供。本地重建的项目不宣称是教师原包。OPEN-003、OPEN-008、OPEN-010 保持原状态；生产 HTTPS/PostgreSQL、应用更新回滚、真实业务恢复与业务用例仍未验证。网站构建结果见构建证据，教师验收和团队签字仍待完成。

Архив преподавателя и исходные замечания отсутствуют; этот проект создан локально и не выдается за оригинал. OPEN-003/008/010 сохраняют статус; HTTPS/PostgreSQL, обновление/откат приложения, бизнес-восстановление и бизнес-кейсы не проверены. Результаты сайта в свидетельствах; приёмка преподавателя и подписи команды ожидаются.

## 历史 История

0.1 为前阶段管理员指南原稿；0.2 是本次九章手册及 Sphinx 站点。所有正式课程文档仍为 DRAFT。

0.1 — прежний черновик администратора; 0.2 — текущие девять глав и сайт Sphinx. Формальные документы остаются DRAFT.
''')
print(json.dumps({'root':str(ROOT),'retained_sources':len(manifest),'admin_blocks':len(blocks)},ensure_ascii=False))
