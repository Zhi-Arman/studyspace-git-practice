from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

STEP = Path(__file__).resolve().parents[1]
PROJECT = STEP.parents[2]
SOURCE = PROJECT / 'coursework/2026-10-21-docs-as-code-environment-v1/08-sphinx-site/project-docs'
PACKAGE = STEP / 'project-docs'
ART = STEP / 'artifacts'
if PACKAGE.exists():
    raise SystemExit('Refusing to overwrite existing project-docs.')
PACKAGE.mkdir()
ART.mkdir(exist_ok=True)
shutil.copy2('/var/folders/ff/kqw394c93dd7krl0z2hcqqdh0000gn/T/codex-clipboard-b1219c9c-bebe-4d1b-971a-2a86410b5988.jpg', ART / 'assignment.jpg')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + '\n', encoding='utf-8')

redactions = []
source_rows = []
names = {'支浩然': '[匿名成员 A]', '俞智文': '[匿名成员 B]', '曹浩然': '[匿名成员 C]', '吕嘉伟': '[匿名成员 D]'}
email = re.compile(r'(?<![\w+/:])\b[\w.+-]+@([\w.-]+\.[A-Za-z]{2,})\b')
secret_patterns = {
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', re.S),
    'github_token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'aws_access_key': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'api_token': re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{25,}\b'),
}

def sanitize(text, rel):
    counts = {}
    for name, replacement in names.items():
        count = text.count(name)
        if count:
            text = text.replace(name, replacement)
            counts['member_names'] = counts.get('member_names', 0) + count
    text, n = re.subn(r'/Users/[^/\s<>"\x00]+', '/local-workspace', text)
    if n: counts['local_user_paths'] = n
    def replace_email(match):
        domain = match.group(1).lower()
        if domain.endswith('.invalid') or domain in ['example.com', 'example.org', 'example.net']:
            return match.group(0)
        counts['email_addresses'] = counts.get('email_addresses', 0) + 1
        return 'contact@example.invalid'
    text = email.sub(replace_email, text)
    for rule, pattern in secret_patterns.items():
        text, n = pattern.subn('[REDACTED_SECRET]', text)
        if n: counts[rule] = n
    if counts: redactions.append({'file': rel, 'counts': counts})
    return text

for src in sorted((SOURCE / 'docs').rglob('*')) + [SOURCE / 'requirements-docs.in', SOURCE / 'requirements-docs.txt']:
    if not src.is_file(): continue
    if src.is_symlink() or '.git' in src.relative_to(SOURCE).parts:
        raise RuntimeError('Source symlink or Git metadata is not allowed')
    rel = src.relative_to(SOURCE)
    dst = PACKAGE / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix == '.docx':
        with ZipFile(src) as zin, ZipFile(dst, 'w', ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.endswith(('.xml', '.rels')):
                    text = sanitize(data.decode('utf-8'), rel.as_posix() + ':' + item.filename)
                    if item.filename == 'docProps/core.xml':
                        xml = ET.fromstring(text)
                        for el in list(xml):
                            if el.tag.rsplit('}', 1)[-1] in ['creator', 'lastModifiedBy']:
                                el.text = ''
                        text = ET.tostring(xml, encoding='unicode')
                    data = text.encode('utf-8')
                zout.writestr(item, data)
    else:
        text = sanitize(src.read_text(encoding='utf-8'), rel.as_posix())
        if rel.as_posix().endswith('source-manifest.json'):
            old = json.loads(text)
            old = {'record_scope': 'HISTORICAL_BEFORE_PACKAGE_REDACTION',
                   'note_zh': '历史哈希仅对应原材料；当前副本以根目录 sources-manifest.json 为准。',
                   'note_ru': 'Исторические хеши относятся к исходникам; текущие копии описаны в sources-manifest.json корня.',
                   'historical_records': old}
            text = json.dumps(old, ensure_ascii=False, indent=2) + '\n'
        write(dst, text)
    source_rows.append({'source': src.relative_to(PROJECT).as_posix(), 'target': rel.as_posix(),
                        'source_sha256': sha(src), 'copy_sha256': sha(dst),
                        'modified_for_privacy_or_record_scope': sha(src) != sha(dst)})

write(PACKAGE / '.gitignore', '''
# 私密配置和身份资料 / Частные настройки и данные
.env
.env.*
!.env.example
.secrets/
secrets/
*.pem
*.key
*.p12
*.pfx
credentials*.json
*personal-data*
# 依赖、缓存及构建输出 / Зависимости, кеш и сборка
/.venv/
/venv/
node_modules/
__pycache__/
*.py[cod]
.pytest_cache/
/site/
/_build/
/build/
/dist/
/artifacts/
*.log
# 明确保留的脱敏历史日志 / Проверенные исторические журналы
!/docs/materials/submission/sphinx-build.log
!/docs/materials/06-architecture-guide/artifacts/foundation-tests.log
# 数据库、备份与本机文件 / БД, копии и локальные файлы
*.db
*.sqlite
*.sqlite3
*.bak
*.zip
*.pdf
.DS_Store
.idea/
.vscode/
~$*
*.tmp
''')
write(PACKAGE / 'build-site.sh', '''
#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p artifacts
DOCS_PYTHON="${DOCS_PYTHON:-.venv/bin/python}"
"$DOCS_PYTHON" -m sphinx -b html -n -W --keep-going -E -a -N \\
  -w artifacts/sphinx-warnings.log docs site 2>&1 | tee artifacts/sphinx-build.log
''')
(PACKAGE / 'build-site.sh').chmod(0o755)
write(PACKAGE / 'STORAGE_POLICY.md', '''
# 文件存储策略

Политика хранения файлов

v1 · DRAFT · 2026-10-21 · LOCAL_ONLY

## 1 纳入版本控制

## 1 Хранить в Git

- Markdown 页面、Sphinx 配置、SVG 图片和 CSS，保持 docs 中的目录层级。
  Markdown, настройки Sphinx, SVG и CSS с сохранением структуры docs.
- requirements-docs.in、带哈希的 requirements-docs.txt、构建脚本与本策略。
  requirements-docs.in, requirements-docs.txt с хешами, скрипт сборки и эта политика.
- docs/materials 中经过脱敏的既有材料；保留两个可编辑 Word 下载件及两个明确列入白名单的历史日志，供原有材料引用使用。
  Обезличенные материалы docs/materials, два редактируемых Word-файла и два разрешённых исторических журнала для ссылок на исходные материалы.
- 来源登记表和当前副本的 SHA-256 清单。历史记录保留其日期与范围，不代表本轮重新执行。
  Реестр источников и SHA-256 текущих копий. Исторические записи сохраняют дату и область и не считаются повторным выполнением.

## 2 排除版本控制

## 2 Исключить из Git

私密 .env、密钥、访问令牌、个人数据、数据库和备份；.venv、node_modules、缓存；site、_build、根 artifacts 中的日志和截图；临时文件、PDF 和压缩包均不入库。

Не хранить частные .env, ключи, токены, персональные данные, БД и резервные копии; .venv, node_modules и кеш; site, _build, журналы и снимки корневой artifacts; временные файлы, PDF и архивы.

`.gitignore` 无法清除已跟踪文件，也无法清理历史中的秘密。每次首次 add 以及后续提交前检查实际候选文件；禁止将别的项目 .git 复制进来。

`.gitignore` не удаляет уже отслеживаемые файлы и секреты из истории. Перед первым add и следующими коммитами проверять фактический список файлов. Не копировать .git другого проекта.

## 3 更新与保存

## 3 Обновление и сохранение

以 .md、.svg、.py 和依赖锁为可编辑源；Word 下载件在对应内容更新后重生成并检查，单文件上限 10 MiB。构建输出可从源重建，不混入源文件提交。A 编辑用户指南，B 编辑管理员指南；当前包尚未执行 git add。

Редактируемые источники — .md, .svg, .py и lock-файлы. После изменения текста Word-файлы создают заново и проверяют; предел одного файла 10 MiB. Результаты сборки восстанавливаются из исходников. A ведёт руководство пользователя, B — администратора. В этом пакете git add ещё не выполнялся.

共享范围为本地课堂练习。原材料保留原样，修改和脱敏仅作用于此副本；向外部发布前重新检查实际内容及权限。

Область обмена — локальное учебное упражнение. Исходные материалы сохраняются, изменения и обезличивание выполняются только в копии. Перед внешней публикацией повторно проверяют содержимое и права.
''')
write(PACKAGE / 'SOURCE_REGISTER.md', '''
# 材料来源登记

Реестр исходных материалов

2026-10-21 · v1 · 自有材料包 / Собственный комплект

采用现有 StudySpace 文档源包，而非教师起始文件夹。原目录为 coursework/2026-10-21-docs-as-code-environment-v1/08-sphinx-site/project-docs；文件级来源和脱敏后哈希见 sources-manifest.json。

Используется собственный комплект документации StudySpace, а не стартовая папка преподавателя. Исходный каталог: coursework/2026-10-21-docs-as-code-environment-v1/08-sphinx-site/project-docs. Источники и хеши копий приведены в sources-manifest.json.

| 材料 / Материал | 随包位置 / Путь | 主题对应 / Тема |
| --- | --- | --- |
| 用户指南 / Руководство пользователя | [docs/user-guide.md](docs/user-guide.md) | 3.4.3 对应沿用已有用户确认 / Сохраняется прежнее подтверждение 3.4.3 |
| 管理员指南及文档站 / Руководство администратора и сайт | [docs/admin-guide.md](docs/admin-guide.md)、[docs/index.md](docs/index.md) | 既有实践 3.4.4 / Прежняя практика 3.4.4 |
| 需求、ADR 与配置资料 / Требования, ADR и настройки | [docs/document-register.md](docs/document-register.md)、docs/materials/00-project/ | 自有既有源材料；3.1–3.3 具体编号映射待课程索引核对 / Собственные исходники; соответствие номерам 3.1–3.3 требует индекса курса |
| 图片与样式 / Изображение и стиль | docs/images/development-chain.svg、docs/_static/coursework.css | 保留原相对路径 / Исходные относительные пути |

当前没有足够证据确认已穷尽教师主题 3.1–3.4 的全部材料，也没有将需求文档中的“3.1”等小节号当作课程主题编号。采用自有材料包后无需用虚构教师包补齐。

Нет оснований утверждать, что собраны все материалы преподавателя тем 3.1–3.4. Номера подразделов вроде «3.1» в требованиях не принимаются за номера тем курса. Использование собственного комплекта не требует вымышленной стартовой папки.
''')
write(PACKAGE / 'README.md', '''
# StudySpace 项目材料源包

Комплект исходных материалов StudySpace

v1 · DRAFT · 2026-10-21 · LOCAL_ONLY · READY_FOR_LOCAL_GIT_REVIEW

本目录包含整理并脱敏的自有文档材料。页面、图片与下载件保持原有相对目录；没有复制任何 .git，也没有在本包执行 git add。3.4.3 与 3.4.4 的已有对应关系保留，3.1–3.3 的课程索引仍待核对。

Здесь собраны и обезличены собственные документы. Сохранены относительные пути страниц, изображений и загрузок. .git не копировался, git add в этом пакете не выполнялся. Соответствие 3.4.3 и 3.4.4 сохранено; индекс тем 3.1–3.3 требует сверки.

## 文件入口

## Основные файлы

- [文档首页 / Главная документации](docs/index.md)
- [A 用户指南 / Руководство пользователя A](docs/user-guide.md)
- [B 管理员指南 / Руководство администратора B](docs/admin-guide.md)
- [文档与下载目录 / Реестр и загрузки](docs/document-register.md)
- [材料来源 / Источники](SOURCE_REGISTER.md)
- [存储策略 / Политика хранения](STORAGE_POLICY.md)
- [当前副本哈希 / Хеши копий](sources-manifest.json)

## 构建文档

## Сборка документации

从本目录运行以下命令；安装依赖可能需要下载网络。本轮直接复用已有文档环境验证构建，未创建新的依赖环境。

Выполнять из этого каталога. Установка может потребовать сеть. При текущей проверке использована уже существующая среда документации, новая среда не создавалась.

```bash
uv venv --python 3.13 .venv
uv pip sync --python .venv/bin/python --require-hashes requirements-docs.txt
bash build-site.sh
```

若本机已经有可用的 Sphinx 环境，可使用 `DOCS_PYTHON` 指向该环境的 Python 后运行构建脚本。生成的 site 和根 artifacts 都被忽略。应用手册中的业务运维命令不属于本次材料整理操作。

Если Sphinx уже установлен в отдельной среде, задайте её Python через DOCS_PYTHON и запустите скрипт. Сгенерированные site и корневая artifacts игнорируются. Команды эксплуатации приложения не входят в текущую подготовку материалов.

## 首次加入 Git 前

## Перед первым добавлением в Git

先阅读 STORAGE_POLICY.md，核查 .gitignore 和待加入文件，确认没有凭据、个人数据、数据库、缓存与生成文件。然后在本练习选定的 A 仓库中按课堂下一步操作；不要移动原项目 .git。本包只准备材料，不代替下一阶段的提交任务。

Прочитайте STORAGE_POLICY.md, проверьте .gitignore и список файлов. Убедитесь в отсутствии секретов, персональных данных, БД, кеша и сгенерированных файлов. Затем продолжайте следующий шаг в выбранном учебном репозитории A. Не переносите .git исходного проекта. Сейчас подготовлены материалы, коммит следующего этапа не подменяется.
''')

manifest = {'version': 1, 'date': '2026-10-21', 'scope': 'LOCAL_ONLY_SANITIZED_COPY',
            'source_root_project_relative': SOURCE.relative_to(PROJECT).as_posix(),
            'copied_files': source_rows,
            'generated_files': ['README.md', '.gitignore', 'STORAGE_POLICY.md', 'SOURCE_REGISTER.md', 'build-site.sh'],
            'redaction_counts': redactions}
write(PACKAGE / 'sources-manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))

links=[]
for path in PACKAGE.rglob('*.md'):
    text=re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
    refs=re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)',text)+re.findall(r'\{download\}`[^`]*<([^>]+)>`',text)
    for ref in refs:
        if ref.startswith(('#','http:','https:','mailto:')):continue
        target=path.parent / unquote(urlsplit(ref).path)
        links.append({'source':path.relative_to(PACKAGE).as_posix(),'reference':ref,'exists':target.exists(),
                      'within_package':target.resolve().is_relative_to(PACKAGE.resolve())})
assert all(x['exists'] and x['within_package'] for x in links), [x for x in links if not x['exists'] or not x['within_package']]
assert not list(PACKAGE.rglob('.git'))

# Validate the planned Git file list using a fresh temporary index outside the package.
with tempfile.TemporaryDirectory(prefix='composition-git-audit-',dir='/private/tmp') as tmp:
    gitdir=Path(tmp)/'empty.git'
    subprocess.run(['git','init','--bare','--initial-branch=main',str(gitdir)],capture_output=True,text=True,check=True)
    base=['git','--git-dir='+str(gitdir),'--work-tree='+str(PACKAGE)]
    candidates=subprocess.run([*base,'ls-files','--others','--exclude-standard','-z'],cwd=PACKAGE,capture_output=True,text=True,check=True).stdout.rstrip('\0').split('\0')
    probes={'.env':True,'.env.local':True,'.secrets/key.txt':True,'server.key':True,'.venv/bin/python':True,
            'node_modules/test.js':True,'site/index.html':True,'_build/index.html':True,'artifacts/check.log':True,
            'app.sqlite3':True,'backup.zip':True,'screenshot.pdf':True,'docs/user-guide.md':False,
            'docs/images/development-chain.svg':False,'docs/materials/submission/sphinx-build.log':False,
            'docs/materials/06-architecture-guide/artifacts/foundation-tests.log':False,
            'docs/materials/artifacts/environment-check.json':False,'README.md':False,'requirements-docs.txt':False}
    ignore_checks=[]
    for path, expected in probes.items():
        result=subprocess.run([*base,'check-ignore','--no-index',path],cwd=PACKAGE,capture_output=True,text=True)
        ignore_checks.append({'path':path,'expected_ignored':expected,'actual_ignored':result.returncode==0,'pass':(result.returncode==0)==expected})
    assert all(p['pass'] for p in ignore_checks)
assert len(candidates)==len([p for p in PACKAGE.rglob('*') if p.is_file()])

remaining=[]
for path in PACKAGE.rglob('*'):
    if not path.is_file():continue
    if path.suffix=='.docx':
        with ZipFile(path) as z:text='\n'.join(z.read(n).decode(errors='replace') for n in z.namelist() if n.endswith(('.xml','.rels')))
    else:text=path.read_text()
    for category,pattern in [('local_user_path',re.compile(r'/Users/[^/\s<>"\x00]+')),*secret_patterns.items()]:
        if pattern.search(text):remaining.append({'file':path.relative_to(PACKAGE).as_posix(),'category':category})
    if any(name in text for name in names):remaining.append({'file':path.relative_to(PACKAGE).as_posix(),'category':'member_name'})
    for m in email.finditer(text):
        if not (m.group(1).lower().endswith('.invalid') or m.group(1).lower() in ['example.com','example.org','example.net']):
            remaining.append({'file':path.relative_to(PACKAGE).as_posix(),'category':'email'})
assert not remaining,remaining
assert all(sha(PROJECT / row['source'])==row['source_sha256'] for row in source_rows)
assert all(sha(PACKAGE / row['target'])==row['copy_sha256'] for row in source_rows)

result={'date':'2026-10-21','scope':'LOCAL_ONLY','copied_files':len(source_rows),'package_files':len(candidates),
        'all_relative_links_valid':True,'relative_links_checked':len(links),'links':links,
        'no_imported_git':True,'git_add_executed':False,'originals_unchanged':True,
        'scan_categories':['local_user_paths','known_member_names','email_addresses','private_keys','github_tokens','aws_access_keys','api_tokens'],
        'scan_remaining_matches':remaining,'scan_note':'Pattern-based privacy check of included text and OOXML; not a certification of absence of all possible secrets.',
        'redactions':redactions,'ignore_checks':ignore_checks,'planned_git_files':candidates,
        'topic_3_1_to_3_3_mapping':'NEEDS_COURSE_INDEX','all_checks_pass':True}
write(ART/'pre-add-verification.json',json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:result[k] for k in ['copied_files','package_files','relative_links_checked','no_imported_git','git_add_executed','originals_unchanged','all_checks_pass']},ensure_ascii=False))
