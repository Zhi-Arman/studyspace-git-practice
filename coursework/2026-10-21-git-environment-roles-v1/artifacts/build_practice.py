from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
A = ROOT / 'participant-a'
B = ROOT / 'participant-b'
ORIGIN = ROOT / 'teaching-origin.git'
GIT = shutil.which('git')
events = []

def run(args, cwd=ROOT):
    env = os.environ.copy()
    env.update({'GIT_TERMINAL_PROMPT': '0', 'LC_ALL': 'C'})
    p = subprocess.run([GIT, *args], cwd=cwd, env=env, capture_output=True, text=True)
    events.append({'cwd': str(cwd.relative_to(ROOT)) if cwd != ROOT else '.',
                   'argv': ['git', *args], 'exit_code': p.returncode,
                   'stdout': p.stdout, 'stderr': p.stderr})
    if p.returncode:
        raise RuntimeError(events[-1])
    return p.stdout.strip()

def write(path, text):
    path.write_text(text.strip() + '\n', encoding='utf-8')

if any(p.exists() for p in (A, B, ORIGIN)):
    raise SystemExit('Practice already exists; refusing to overwrite repositories.')
ART.mkdir(exist_ok=True)
SOURCE_IMAGE = Path('/var/folders/ff/kqw394c93dd7krl0z2hcqqdh0000gn/T/codex-clipboard-c37eb453-3c7f-4cfa-b393-d8f512f18dd5.jpg')
shutil.copy2(SOURCE_IMAGE, ART / 'assignment.jpg')
version = run(['--version'])
run(['init', '--bare', '--initial-branch=main', str(ORIGIN)])
run(['init', '--initial-branch=main', str(A)])
for key, value in [('user.name', 'Participant A (local exercise)'),
                   ('user.email', 'participant-a@example.invalid'),
                   ('commit.gpgsign', 'false')]:
    run(['config', '--local', key, value], A)

write(A / '.gitignore', '.DS_Store')
write(A / 'README.md', '''
# Git 双人文档练习

Парная учебная работа с документацией в Git

2026-10-21 · v1 · LOCAL_DEMO

A 编辑 user-guide.md；B 编辑 admin-guide.md。两个提交身份均为本机练习角色。

A редактирует user-guide.md, B — admin-guide.md. Обе подписи коммитов являются локальными учебными ролями.

平台选择 GitHub；本练习 origin 是本地裸仓库 teaching-origin.git。线上仓库尚未创建。

Выбрана платформа GitHub. В упражнении origin — локальный bare-репозиторий teaching-origin.git. Репозиторий GitHub пока не создан.

本目录只含文档，不包含 StudySpace 业务实现。练习说明与结果在上一级 README.md。

Здесь только документация, без реализации бизнес-функций StudySpace. Порядок и результаты — в README.md родительской папки.
''')
write(A / 'user-guide.md', '''
# Markdown 用户指南

Руководство пользователя Markdown

Version 1 · DRAFT · 2026-10-21 · 负责人 A / Ответственный A

面向首次编辑本练习文档的学生，说明文件编辑、保存与预览。

Для студентов, впервые редактирующих материалы упражнения. Описаны редактирование, сохранение и предпросмотр.
''')
write(A / 'admin-guide.md', '''
# Git 练习管理员指南

Руководство администратора учебного репозитория Git

Version 1 · DRAFT · 2026-10-21 · 负责人 B / Ответственный B

管理员负责维护学习仓库、核对分工并确认同步状态。

Администратор поддерживает учебный репозиторий, проверяет распределение файлов и синхронизацию.
''')
run(['add', 'README.md', 'user-guide.md', 'admin-guide.md', '.gitignore'], A)
run(['commit', '-m', 'docs: initialize bilingual guide practice'], A)
initial = run(['rev-parse', 'HEAD'], A)
run(['remote', 'add', 'origin', str(ORIGIN)], A)
run(['push', '-u', 'origin', 'main'], A)
run(['clone', '--no-hardlinks', str(ORIGIN), str(B)])
for key, value in [('user.name', 'Participant B (local exercise)'),
                   ('user.email', 'participant-b@example.invalid'),
                   ('commit.gpgsign', 'false')]:
    run(['config', '--local', key, value], B)
clone_head = run(['rev-parse', 'HEAD'], B)

with (A / 'user-guide.md').open('a', encoding='utf-8') as f:
    f.write('''

## 1 编辑与保存

## 1 Редактирование и сохранение

1. 在 VS Code 打开 participant-a 学习仓库，选择 user-guide.md。
   Откройте participant-a в VS Code и выберите user-guide.md.
2. 在标题和正文中成对保留中文与俄语，保存文件。
   Сохраняйте китайский и русский текст рядом в заголовках и абзацах, затем сохраните файл.
3. 执行 git diff -- user-guide.md，确认差异只包含本人的预期修改。
   Выполните git diff -- user-guide.md и убедитесь, что изменения соответствуют вашей задаче.

## 2 预览与提交

## 2 Предпросмотр и коммит

1. 使用 VS Code 命令 Markdown: Open Preview to the Side，检查标题和正文显示。
   Откройте Markdown: Open Preview to the Side и проверьте заголовки и текст.
2. 依次执行下列命令，将当前指南提交到练习仓库。
   Последовательно выполните команды для коммита руководства в учебный репозиторий.

```bash
git add user-guide.md
git commit -m "docs: add user guide editing steps"
git push origin main
git status --short
```

本轮实际验证 Git 命令；VS Code 界面操作留给参与者本人检查。

В этом запуске проверены команды Git. Действия в интерфейсе VS Code участник проверяет самостоятельно.
''')
run(['diff', '--check'], A)
run(['diff', '--', 'user-guide.md'], A)
run(['add', 'user-guide.md'], A)
run(['commit', '-m', 'docs: add user guide editing steps'], A)
a_edit = run(['rev-parse', 'HEAD'], A)
run(['push', 'origin', 'main'], A)
run(['pull', '--ff-only', 'origin', 'main'], B)
with (B / 'admin-guide.md').open('a', encoding='utf-8') as f:
    f.write('''

## 1 仓库准备与分工

## 1 Подготовка репозитория и роли

初始仓库由 A 创建并先提交两份指南；B 在初始提交可获取后克隆。本轮通过本地裸仓库交换提交，选定的线上平台是 GitHub。

A создаёт исходный репозиторий и первый коммит с двумя руководствами. B клонирует его после первого коммита. Сейчас обмен выполняется через локальный bare-репозиторий; выбранная онлайн-платформа — GitHub.

A 维护 user-guide.md，B 维护 admin-guide.md；各自执行命令并检查当前目录、身份和修改范围。

A ведёт user-guide.md, B — admin-guide.md. Каждый выполняет команды и проверяет каталог, подпись и изменяемые файлы.

## 2 同步和检查

## 2 Синхронизация и проверка

在 B 仓库中，先同步 A 的提交，再保存本人的指南修改并执行：

В репозитории B сначала получите коммит A, затем сохраните свои изменения руководства и выполните:

```bash
git diff -- admin-guide.md
git add admin-guide.md
git commit -m "docs: add admin guide repository checks"
git push origin main
git status --short
git log --oneline -3
```

git status --short 无输出表示工作区干净。核对 A、B 的 git rev-parse HEAD，应在完成同步后得到相同提交号。

Пустой вывод git status --short означает чистое рабочее дерево. После синхронизации git rev-parse HEAD у A и B должен совпасть.

## 3 常见问题

## 3 Частые затруднения

若出现“not a git repository”，先检查 pwd；若提示缺少作者身份，仅在本学习仓库用 git config --local 设置自己的姓名和邮箱。若推送被拒绝，先检查 git status，再联系伙伴并同步，避免强制推送。

При «not a git repository» проверьте pwd. Если не задан автор, задайте своё имя и почту через git config --local только в учебном репозитории. При отклонённом push проверьте git status, согласуйте действия с партнёром и синхронизируйтесь без принудительного push.
''')
run(['diff', '--check'], B)
run(['diff', '--', 'admin-guide.md'], B)
run(['add', 'admin-guide.md'], B)
run(['commit', '-m', 'docs: add admin guide repository checks'], B)
b_edit = run(['rev-parse', 'HEAD'], B)
run(['push', 'origin', 'main'], B)
run(['pull', '--ff-only', 'origin', 'main'], A)

checks = []
def check(name, ok):
    checks.append({'name': name, 'pass': bool(ok)})

check('B cloned initial commit before role edits', clone_head == initial)
heads = {}
for label, repo in [('A', A), ('B', B)]:
    heads[label] = run(['rev-parse', 'HEAD'], repo)
    check(f'{label} isolated Git top level', Path(run(['rev-parse', '--show-toplevel'], repo)) == repo)
    check(f'{label} clean working tree', run(['status', '--porcelain'], repo) == '')
    check(f'{label} identity is local exercise role', '(local exercise)' in run(['config', '--local', '--get', 'user.name'], repo))
    check(f'{label} main branch', run(['branch', '--show-current'], repo) == 'main')
    check(f'{label} local origin', run(['remote', 'get-url', 'origin'], repo) == str(ORIGIN))
    check(f'{label} has exactly three exercise commits', run(['rev-list', '--count', 'HEAD'], repo) == '3')
    run(['fsck', '--no-reflogs'], repo)
    for filename in ['README.md', 'user-guide.md', 'admin-guide.md']:
        check(f'{label} {filename} exists', (repo / filename).is_file())
check('A role commit changes only user-guide.md', run(['diff-tree', '--no-commit-id', '--name-only', '-r', a_edit], A) == 'user-guide.md')
check('B role commit changes only admin-guide.md', run(['diff-tree', '--no-commit-id', '--name-only', '-r', b_edit], B) == 'admin-guide.md')
check('A and B synchronized', heads['A'] == heads['B'] == b_edit)
check('bare remote synchronized', run(['rev-parse', 'refs/heads/main'], ORIGIN) == b_edit)
check('origin is bare', run(['rev-parse', '--is-bare-repository'], ORIGIN) == 'true')
for filename in ['user-guide.md', 'admin-guide.md']:
    check(f'{filename} contents identical after sync', (A / filename).read_bytes() == (B / filename).read_bytes())

evidence = {'date': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
            'git_executable': GIT, 'git_version': version, 'root': str(ROOT),
            'mode': 'LOCAL_DEMO', 'selected_online_platform': 'GitHub',
            'online_repository': 'NOT_CREATED', 'human_independent_execution': 'NOT_VERIFIED',
            'initial_commit': initial, 'a_edit_commit': a_edit, 'b_edit_commit': b_edit,
            'heads': heads, 'checks': checks, 'all_pass': all(c['pass'] for c in checks),
            'commands': events}
write(ART / 'execution.json', json.dumps(evidence, ensure_ascii=False, indent=2))
log = []
for e in events:
    log.extend([f"[{e['cwd']}] $ {' '.join(e['argv'])}", e['stdout'].rstrip(), e['stderr'].rstrip(), f"exit={e['exit_code']}", ''])
write(ART / 'commands.log', '\n'.join(log))
assert evidence['all_pass']
print(json.dumps({'git_version': version, 'checks': len(checks), 'all_pass': evidence['all_pass'], 'head': b_edit}, ensure_ascii=False))
