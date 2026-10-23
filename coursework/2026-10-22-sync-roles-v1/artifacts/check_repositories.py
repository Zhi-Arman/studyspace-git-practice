from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
PREVIOUS = PROJECT / 'coursework/2026-10-21-git-environment-roles-v1'
ORIGIN = PREVIOUS / 'teaching-origin.git'
REVIEWER = ROOT / 'reviewer'
commands = []
checks = []

def run(cwd, *args, ok=True):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    commands.append(dict(cwd=str(cwd), argv=list(args), exit_code=p.returncode,
                         stdout=p.stdout, stderr=p.stderr))
    if ok and p.returncode:
        raise RuntimeError(commands[-1])
    return p.stdout.strip()

def check(name, condition):
    checks.append(dict(name=name, passed=bool(condition)))
    assert condition, name

def source_hashes():
    return {str(p.relative_to(PREVIOUS)): hashlib.sha256(p.read_bytes()).hexdigest()
            for n in ('participant-a', 'participant-b') for p in sorted((PREVIOUS/n).iterdir())
            if p.is_file()}

before_files = source_hashes()
main_before = run(PROJECT, 'git', 'rev-parse', 'HEAD')
tracked_before = run(PROJECT, 'git', 'diff', 'HEAD', '--')
root_status = run(PROJECT, 'git', 'status', '--short', '--branch')
root_remote = run(PROJECT, 'git', 'remote', '-v')
version = run(PROJECT, 'git', '--version')
origin_head = run(PROJECT, 'git', '--git-dir='+str(ORIGIN), 'rev-parse', 'refs/heads/main')
run(PROJECT, 'git', '--git-dir='+str(ORIGIN), 'fsck', '--full')
check('shared repository main exists', len(origin_head) == 40)

repos = {}
for label in ('participant-a', 'participant-b'):
    path = PREVIOUS / label
    check(label+' initial worktree clean', run(path, 'git', 'status', '--porcelain=v1', '--untracked-files=all') == '')
    check(label+' local shared origin', Path(run(path, 'git', 'remote', 'get-url', 'origin')).resolve() == ORIGIN.resolve())
    run(path, 'git', 'fetch', '--no-prune', 'origin')
    check(label+' main checked out', run(path, 'git', 'branch', '--show-current') == 'main')
    head = run(path, 'git', 'rev-parse', 'HEAD')
    check(label+' main matches shared main', head == origin_head)
    check(label+' origin/main freshly matches shared main', run(path, 'git', 'rev-parse', 'origin/main') == origin_head)
    check(label+' no ahead or behind commits', run(path, 'git', 'rev-list', '--left-right', '--count', 'main...origin/main').split() == ['0', '0'])
    check(label+' final worktree clean', run(path, 'git', 'status', '--porcelain=v1', '--untracked-files=all') == '')
    run(path, 'git', 'fsck', '--full')
    repos[label] = dict(path=str(path), head=head, status='CLEAN', ahead=0, behind=0,
                        configured_author=run(path, 'git', 'config', '--local', '--get', 'user.name'))

if not REVIEWER.exists():
    run(ROOT, 'git', 'clone', '--no-hardlinks', '--branch', 'main', str(ORIGIN), str(REVIEWER))
check('reviewer worktree clean', run(REVIEWER, 'git', 'status', '--porcelain=v1', '--untracked-files=all') == '')
check('reviewer main checked out', run(REVIEWER, 'git', 'branch', '--show-current') == 'main')
check('reviewer main matches shared main', run(REVIEWER, 'git', 'rev-parse', 'HEAD') == origin_head)
check('reviewer has independent Git directory', (REVIEWER/'.git').is_dir())
run(REVIEWER, 'git', 'fsck', '--full')
repos['reviewer'] = dict(path=str(REVIEWER), head=origin_head, status='CLEAN')
check('previous A and B files preserved', before_files == source_hashes())
check('StudySpace main commit preserved', run(PROJECT, 'git', 'rev-parse', 'HEAD') == main_before)
check('StudySpace tracked changes preserved', run(PROJECT, 'git', 'diff', 'HEAD', '--') == tracked_before)
check('shared main preserved', run(PROJECT, 'git', '--git-dir='+str(ORIGIN), 'rev-parse', 'refs/heads/main') == origin_head)

shutil.copy2('/var/folders/ff/kqw394c93dd7krl0z2hcqqdh0000gn/T/codex-clipboard-6cb30311-c1a8-4c06-92bf-e21d1ed45e26.jpg', ROOT/'artifacts/task.jpg')
result = dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
              status='LOCAL_DEMO', git_version=version, shared_repository=str(ORIGIN),
              shared_main=origin_head, repositories=repos,
              project=dict(path=str(PROJECT), head=main_before, status_before=root_status,
                           remote=root_remote, worktree_clean=False),
              checks=checks, commands=commands,
              human_execution='NOT_VERIFIED', online_repository_access='NOT_VERIFIED',
              business_tests='NOT_RUN', branch_protection='NOT_CONFIGURED')
(ROOT/'artifacts/verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(dict(passed=sum(x['passed'] for x in checks), total=len(checks),
                     shared_main=origin_head, repositories=repos),ensure_ascii=False,indent=2))
