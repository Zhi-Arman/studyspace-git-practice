import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / 'artifacts'
REPO = Path('/Users/zhi/Documents/软件生命周期/git-practice/lab-git')
ENV = dict(os.environ, GIT_MERGE_AUTOEDIT='no', LC_ALL='en_US.UTF-8')
records = []

def run(stage, *args, expected=0):
    p = subprocess.run(args, cwd=REPO, env=ENV, text=True, capture_output=True)
    record = dict(stage=stage, command=shlex.join(args), returncode=p.returncode,
                  stdout=p.stdout, stderr=p.stderr,
                  time=datetime.datetime.now(datetime.timezone.utc).isoformat())
    records.append(record)
    (A/'commands.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    text = '\n\n'.join(f"## {x['stage']}\n\n```console\n$ {x['command']}\n{x['stdout']}{x['stderr']}\n[exit {x['returncode']}]\n```" for x in records)
    (ROOT/'终端实际操作记录.md').write_text('# Git 终端实际操作记录\n\n' + text + '\n')
    if p.returncode != expected:
        raise RuntimeError(record)
    return p.stdout.strip()

assert run('baseline', 'git', 'status', '--porcelain') == ''
assert run('baseline', 'git', 'branch', '--show-current') == 'main'
assert run('baseline', 'git', 'rev-list', '--count', 'HEAD') == '1'
initial = run('baseline', 'git', 'rev-parse', 'HEAD')
initial_readme = (REPO/'readme.txt').read_bytes()
assert initial.startswith('97d036d')
run('baseline', 'git', 'show', '--no-patch', '--format=fuller', 'HEAD')
run('baseline', 'git', 'bundle', 'create', str(A/'task1-before.bundle'), '--all')

run('task2', 'git', 'branch', 'feature-a')
run('task2', 'git', 'switch', 'feature-a')
run('task2', '/bin/zsh', '-c', 'printf "%s\\n" "Функция A" > a.txt')
run('task2', 'git', 'add', 'a.txt')
run('task2', 'git', 'commit', '-m', 'Добавлена функция A')
run('task2', 'git', 'switch', 'main')
assert not (REPO/'a.txt').exists()
run('task2', 'git', 'merge', 'feature-a')
task2_graph = run('task2', 'git', 'log', '--oneline', '--graph', '--decorate')
(A/'task2-history.txt').write_text(task2_graph+'\n')
assert run('task2', 'git', 'rev-list', '--count', 'HEAD') == '2'
assert run('task2', 'cat', 'a.txt') == 'Функция A'

run('task3', '/bin/zsh', '-c', 'printf "%s\\n" "Цена: 100 рублей" > price.txt')
run('task3', 'git', 'add', 'price.txt')
run('task3', 'git', 'commit', '-m', 'Добавлена цена')
run('task3', 'git', 'branch', 'price-up')
run('task3', 'git', 'branch', 'price-promo')
run('task3', 'git', 'switch', 'price-up')
run('task3', '/bin/zsh', '-c', 'printf "%s\\n" "Цена: 120 рублей" > price.txt')
run('task3', 'git', 'commit', '-am', 'Повышена цена')
run('task3', 'git', 'switch', 'price-promo')
assert run('task3', 'cat', 'price.txt') == 'Цена: 100 рублей'
run('task3', '/bin/zsh', '-c', 'printf "%s\\n" "Цена: 90 рублей" > price.txt')
run('task3', 'git', 'commit', '-am', 'Акционная цена')
run('task3', 'git', 'switch', 'main')
run('task3', 'git', 'merge', 'price-up')
assert run('task3', 'cat', 'price.txt') == 'Цена: 120 рублей'
conflict_output = run('task3 expected conflict', 'git', 'merge', 'price-promo', expected=1)
assert 'CONFLICT' in conflict_output
conflict_text = (REPO/'price.txt').read_text()
assert '<<<<<<< HEAD' in conflict_text and '>>>>>>> price-promo' in conflict_text
(A/'price-conflict.txt').write_text(conflict_text)
(A/'conflict-status.txt').write_text(run('task3 conflict evidence', 'git', 'status')+'\n')
assert run('task3 conflict evidence', 'git', 'ls-files', '-u')
run('task3 resolve', '/bin/zsh', '-c', 'printf "%s\\n" "Цена: 90 рублей" > price.txt')
run('task3 resolve', 'git', 'add', 'price.txt')
run('task3 resolve', 'git', 'commit', '-m', 'Разрешён конфликт цены')
merge_commit = run('task3 verify', 'git', 'rev-parse', 'HEAD')
assert len(run('task3 verify', 'git', 'show', '-s', '--format=%P', 'HEAD').split()) == 2
assert run('task3 verify', 'git', 'ls-files', '-u') == ''
(A/'task3-history.txt').write_text(run('task3 verify', 'git', 'log', '--oneline', '--graph', '--decorate')+'\n')

run('task4', 'git', 'tag', 'v1.0.0')
run('task4', 'git', 'switch', '-c', 'update-readme')
run('task4', '/bin/zsh', '-c', 'printf "\\n%s\\n" "Практикум Git: создание веток, слияние и разрешение конфликтов." >> readme.txt')
run('task4', 'git', 'diff', '--', 'readme.txt')
run('task4', 'git', 'add', 'readme.txt')
run('task4', 'git', 'commit', '-m', 'Обновлено описание практикума')
readme_commit = run('task4', 'git', 'rev-parse', 'HEAD')
(A/'readme-change.diff').write_text(run('task4 verify', 'git', 'diff', 'main...update-readme')+'\n')
assert run('task4 verify', 'git', 'diff', '--name-only', 'main...update-readme') == 'readme.txt'
run('final', 'git', 'switch', 'main')
graph = run('final', 'git', 'log', '--oneline', '--graph', '--decorate', '--all')
(A/'final-history.txt').write_text(graph+'\n')
branches = run('final', 'git', 'branch', '--list').splitlines()
run('final', 'git', 'tag', '--list')
run('final', 'git', 'status')
checks = {
    'task1_original_commit_preserved': run('verify', 'git', 'rev-list', '--max-parents=0', 'main') == initial,
    'task1_readme_preserved_on_main': (REPO/'readme.txt').read_bytes() == initial_readme,
    'task2_two_commits_at_merge': len(task2_graph.splitlines()) == 2,
    'task2_a_txt_on_main': (REPO/'a.txt').read_text() == 'Функция A\n',
    'task3_real_conflict_recorded': 'CONFLICT' in conflict_output,
    'task3_final_price_90': (REPO/'price.txt').read_text() == 'Цена: 90 рублей\n',
    'task3_no_conflict_markers': '<<<<<<<' not in (REPO/'price.txt').read_text(),
    'task3_no_unmerged_paths': run('verify', 'git', 'ls-files', '-u') == '',
    'task4_tag_points_to_merge': run('verify', 'git', 'rev-parse', 'v1.0.0') == merge_commit,
    'task4_one_readme_commit': run('verify', 'git', 'rev-list', '--count', 'main..update-readme') == '1',
    'final_main': run('verify', 'git', 'branch', '--show-current') == 'main',
    'final_clean': run('verify', 'git', 'status', '--porcelain') == '',
    'no_remote_configured': run('verify', 'git', 'remote') == '',
}
assert all(checks.values()), checks
result = dict(repo=str(REPO), initial_commit=initial, merge_commit=merge_commit,
              readme_commit=readme_commit, checks=checks, all_pass=all(checks.values()),
              main_commit_count=run('verify', 'git', 'rev-list', '--count', 'main'),
              branches=branches, graph=graph, remote_pr='NOT_CREATED_NOT_REQUIRED_BY_IMAGES',
              user_task1_commands='NOT_REPLAYED', date='2026-10-22', timezone='Asia/Shanghai')
(A/'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
run('archive', 'git', 'bundle', 'create', str(A/'completed-repository.bundle'), '--all')
print(json.dumps(result, ensure_ascii=False, indent=2))
