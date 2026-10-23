from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
REPO='Zhi-Arman/studyspace-git-practice'
A=ROOT/'author-a';B=ROOT/'author-b'
FILE='docs/build-check.md'
BASE_COMMAND='.venv/bin/python -m sphinx -b html docs site\n'
A_COMMAND='.venv/bin/python -m sphinx -W -b html docs site\n'
B_COMMAND='.venv/bin/python -m sphinx -n -b html docs site\n'
commands=[];checks=[]
def run(cwd,*argv):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
    commands.append(dict(cwd=str(cwd),argv=list(argv),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode:raise RuntimeError(commands[-1])
    return p.stdout.strip()
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)));assert value,name
def identity(path):
    for key in ('user.name','user.email'):
        value=subprocess.check_output(['git','config','--local','--get',key],cwd=PROJECT,text=True).strip()
        subprocess.run(['git','config','--local',key,value],cwd=path,check=True)

check('new isolated workspaces',not A.exists() and not B.exists())
root_head=run(PROJECT,'git','rev-parse','HEAD')
run(ROOT,'gh','repo','clone',REPO,str(A),'--','--branch','main')
identity(A)
run(A,'git','fetch','--no-prune','origin')
run(A,'git','pull','--ff-only','origin','main')
original=run(A,'git','rev-parse','HEAD')
check('fresh main matches GitHub',original==run(A,'git','ls-remote','origin','refs/heads/main').split()[0])
check('initial main clean',run(A,'git','status','--porcelain')=='')
old_files=run(A,'git','ls-tree','-r','--name-only','HEAD').splitlines()
source_hashes={n:hashlib.sha256((A/n).read_bytes()).hexdigest() for n in old_files}
check('exercise file does not overwrite existing file',FILE not in old_files)
check('exercise branch names unused',run(A,'git','ls-remote','origin','refs/heads/docs/conflict-base','refs/heads/docs/conflict-a','refs/heads/docs/conflict-b')=='')
run(A,'git','switch','-c','docs/conflict-base')
(A/'docs').mkdir(exist_ok=True)
(A/FILE).write_text(BASE_COMMAND)
run(A,'git','add','--',FILE)
run(A,'git','commit','-m','docs: add controlled conflict build command baseline')
base=run(A,'git','rev-parse','HEAD')
run(A,'git','push','-u','origin','docs/conflict-base')
run(A,'git','switch','-c','docs/conflict-a',base)
(A/FILE).write_text(A_COMMAND)
run(A,'git','diff','--check')
check('A changes only the command line',run(A,'git','diff','--numstat')=='1\t1\t'+FILE)
(ROOT/'artifacts/a.diff').write_text(run(A,'git','diff','--',FILE)+'\n')
run(A,'git','add','--',FILE)
run(A,'git','commit','-m','docs: treat Sphinx warnings as errors in A branch')
a_head=run(A,'git','rev-parse','HEAD')
run(A,'git','push','-u','origin','docs/conflict-a')

run(ROOT,'gh','repo','clone',REPO,str(B),'--','--branch','docs/conflict-base')
identity(B)
check('B starts at common baseline',run(B,'git','rev-parse','HEAD')==base)
run(B,'git','switch','-c','docs/conflict-b',base)
(B/FILE).write_text(B_COMMAND)
run(B,'git','diff','--check')
check('B changes only the command line',run(B,'git','diff','--numstat')=='1\t1\t'+FILE)
(ROOT/'artifacts/b.diff').write_text(run(B,'git','diff','--',FILE)+'\n')
run(B,'git','add','--',FILE)
run(B,'git','commit','-m','docs: enable nitpicky Sphinx checks in B branch')
b_head=run(B,'git','rev-parse','HEAD')
run(B,'git','push','-u','origin','docs/conflict-b')
run(A,'git','fetch','--no-prune','origin')
check('A parent is shared baseline',run(A,'git','rev-parse',a_head+'^')==base)
check('B parent is shared baseline',run(A,'git','rev-parse',b_head+'^')==base)
check('A B merge-base is shared baseline',run(A,'git','merge-base',a_head,b_head)==base)
check('baseline has exactly one command line',run(A,'git','show',base+':'+FILE)+'\n'==BASE_COMMAND)
check('A worktree clean',run(A,'git','status','--porcelain')=='')
check('B worktree clean',run(B,'git','status','--porcelain')=='')
check('GitHub main unchanged before A merge',run(A,'git','ls-remote','origin','refs/heads/main').split()[0]==original)
check('prior shared files preserved',all(hashlib.sha256((A/n).read_bytes()).hexdigest()==h for n,h in source_hashes.items()))
shutil.copy2('/var/folders/ff/kqw394c93dd7krl0z2hcqqdh0000gn/T/codex-clipboard-0af257af-d35d-487d-b9d7-afe1aabfec77.jpg',ROOT/'artifacts/task.jpg')
result=dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),repository=REPO,
            mode='SINGLE_ACCOUNT_AUTOMATED_ROLE_DEMO',actor='Zhi-Arman',role_A='支浩然',role_B='俞智文',
            original_main=original,root_project_head=root_head,common_base=base,a_head=a_head,b_head=b_head,
            file=FILE,baseline_command=BASE_COMMAND,a_command=A_COMMAND,b_command=B_COMMAND,
            build_execution='NOT_RUN',business_tests='NOT_RUN',human_execution='NOT_VERIFIED',
            source_hashes=source_hashes,checks=checks,commands=commands)
(ROOT/'artifacts/preparation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for role,branch,head in [('A','docs/conflict-a',a_head),('B','docs/conflict-b',b_head)]:
    body=f'''## Goal
Complete the controlled merge-conflict exercise in the shared classroom repository.

## Changes
Add the shared baseline `docs/build-check.md` from commit `{base}`, then change only its one command line on `{branch}`.
The role {role} commit is `{head}`. A enables `-W`; B enables `-n` in the same line.

## Validation
- A and B branches have exactly the same parent `{base}`.
- Each role changes only one line in `docs/build-check.md` relative to that parent.
- `git diff --check` passed and both published worktrees are clean.

## Workflow
Merge A first. Then attempt B into the updated main and preserve the expected conflict without resolving or aborting it. Keep all exercise branches.

## Limitations
This is the user's authorized single-account automated A/B role demonstration using `Zhi-Arman`, not personal execution or independent approval by students. Sphinx commands are exercise text only: the shared repository has no full Sphinx configuration, so build execution and business tests are NOT_RUN.
'''
    (ROOT/f'artifacts/pr-{role.lower()}-body.md').write_text(body)
print(json.dumps({k:result[k] for k in ('original_main','common_base','a_head','b_head')},indent=2))
print('Preparation checks passed:',len(checks),'/',len(checks))
