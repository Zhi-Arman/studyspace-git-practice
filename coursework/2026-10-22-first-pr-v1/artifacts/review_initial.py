from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'reviewer-b'
commands=[]
def run(cwd,*argv):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
    commands.append(dict(cwd=str(cwd),argv=list(argv),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode:raise RuntimeError(commands[-1])
    return p.stdout.strip()
if not B.exists():run(ROOT,'gh','repo','clone','Zhi-Arman/studyspace-git-practice',str(B),'--','--branch','docs/preview')
run(B,'git','fetch','--no-prune','origin')
assert run(B,'git','status','--porcelain')==''
assert run(B,'git','diff','--name-only','origin/main...HEAD')=='user-guide.md'
run(B,'git','diff','--check','origin/main...HEAD')
patch=run(B,'git','diff','origin/main...HEAD','--','user-guide.md')
source=(B/'user-guide.md').read_text()
assert 'git push -u origin docs/preview' in source
assert 'git branch --show-current' not in source
review='''B-role automated review (single-account classroom demonstration, not an independent student review).

Please add a current-branch check before `git add`. The new push command targets `docs/preview`, but `git commit` still runs on whichever branch is checked out. State in both Chinese and Russian that `git branch --show-current` must output `docs/preview` and that the user must stop if it does not. This prevents committing on `main` while pushing a different branch.'''
payload=dict(commit_id=run(B,'git','rev-parse','HEAD'),event='COMMENT',body=review,
             comments=[dict(path='user-guide.md',line=35,side='RIGHT',body=review)])
(ROOT/'artifacts/review-request.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
(ROOT/'artifacts/review-initial.json').write_text(json.dumps(dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),mode='SINGLE_ACCOUNT_AUTOMATED_ROLE_DEMO',patch=patch,commands=commands,finding=review),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(payload,ensure_ascii=False,indent=2))
