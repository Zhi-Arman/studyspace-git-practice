from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
B = ROOT.parent / '2026-10-22-controlled-conflict-v1/author-b'
A = B.parent / 'author-a'
REPO = 'Zhi-Arman/studyspace-git-practice'
COMMAND = '.venv/bin/python -m sphinx -W -n -b html docs site'
RESOLUTION = '49de18441048777347d9c008e5ba4fe3149be977'
BASE = '31622e8f11087615f47c301c9c43f276b3d3fe11'

def save(name, value):
    (ART / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def run(args, cwd=B, allowed=(0,)):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    item = dict(at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(), cwd=str(cwd), argv=args,
                exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    with (ART / 'commands.jsonl').open('a') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
    assert p.returncode in allowed, item
    return p.stdout.strip()

def gh(args):
    return json.loads(run(['gh', 'api'] + args))

def validate(label):
    diff = run(['git', 'diff', '--check'])
    unmerged = run(['git', 'ls-files', '-u'])
    assert not unmerged
    scan = run(['git', 'grep', '-n', '-E', '^(<{7}|={7}|>{7})( |$)', '--', '*.md'], allowed=(1,))
    assert not scan
    assert (B / 'docs/build-check.md').read_text() == COMMAND + '\n'
    run(['uv', '--cache-dir', str(ART / 'uv-cache'), 'pip', 'check', '--python', '.venv/bin/python'])
    output = run(COMMAND.split())
    (ART / (label + '-sphinx-build.log')).write_text(output + '\n')
    assert 'build succeeded.' in output and 'WARNING:' not in output
    html = (B / 'site/index.html').read_text()
    assert '冲突解决记录' in html and 'Запись о разрешении конфликта' in html
    result = dict(diff_check='PASS', unmerged_index='EMPTY', tracked_markdown_marker_scan='PASS',
                  marker_scan_expected_exit=1, build_exit_code=0, warnings=0,
                  command=COMMAND, html=str(B / 'site/index.html'))
    save(label + '-validation.json', result)
    return result

def prepare():
    assert run(['git', 'status', '--porcelain=v1']) == ''
    assert run(['git', 'rev-parse', 'HEAD']) == BASE
    save('before.json', dict(base=BASE, resolution=RESOLUTION,
         branch=run(['git', 'branch', '--show-current']),
         branches=run(['git', 'branch', '-avv']), main_status=run(['git', 'status', '--short', '--branch'])))
    run(['git', 'switch', 'docs/conflict-b'])
    run(['git', 'merge', '--ff-only', 'main'])
    run(['git', 'merge-base', '--is-ancestor', RESOLUTION, 'HEAD'])
    p = B / 'docs/index.md'
    old = p.read_text()
    (ART / 'index-before.md').write_text(old)
    section = '''## 3 冲突解决记录

3 Запись о разрешении конфликта

A 与 B 从同一提交修改 docs/build-check.md 的唯一一行：A 加入 -W，B 加入 -n。A 先合并后，B 合并时发生真实冲突；最终保留两个参数，完整命令见第 2 节。

A и B изменили единственную строку docs/build-check.md от одного коммита: A добавил -W, B добавил -n. После слияния A попытка слияния B вызвала реальный конфликт; итог сохраняет оба параметра, полная команда приведена в разделе 2.

冲突在 PR #3 中解决并合并；本节继续记录该解决方案的文档审查。提交前执行 git diff --check 与 git ls-files -u。

Конфликт разрешён и слит в PR #3; этот раздел продолжает рецензию документации решения. Перед коммитом выполните git diff --check и git ls-files -u.

'''
    old = old.replace('## 4 管理员指南\n\n4 Руководство администратора', '## 5 管理员指南\n\n5 Руководство администратора')
    old = old.replace('## 3 用户指南\n\n3 Руководство пользователя', section + '## 4 用户指南\n\n4 Руководство пользователя')
    assert old.count('## 3 冲突解决记录') == 1
    p.write_text(old)
    finish_initial()

def finish_initial():
    p = B / 'docs/index.md'
    assert run(['git', 'branch', '--show-current']) == 'docs/conflict-b'
    assert run(['git', 'rev-parse', 'HEAD']) == BASE
    assert run(['git', 'diff', '--name-only']) == 'docs/index.md'
    validate('initial')
    (ART / 'initial.diff').write_text(run(['git', 'diff', '--', 'docs/index.md']) + '\n')
    run(['git', 'add', '--', 'docs/index.md'])
    run(['git', 'commit', '-m', 'docs: document resolved build-check conflict for second review'])
    head = run(['git', 'rev-parse', 'HEAD'])
    assert run(['git', 'diff', '--name-only', BASE, head]) == 'docs/index.md'
    save('initial.json', dict(base=BASE, resolution=RESOLUTION, head=head, branch='docs/conflict-b',
                             line=next(i for i,s in enumerate(p.read_text().splitlines(),1) if s.startswith('冲突在 PR #3'))))
    print(head)

if __name__ == '__main__':
    prepare()
