from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[1]
PREVIOUS=PROJECT/'coursework/2026-10-22-controlled-conflict-v1'
OLD=json.loads((PREVIOUS/'artifacts/execution.json').read_text())
L=json.loads((ROOT/'artifacts/local-resolution.json').read_text())
A=PREVIOUS/'author-a';B=Path(L['working_directory'])
REPO='Zhi-Arman/studyspace-git-practice';END='repos/'+REPO+'/pulls/3'
R=L['resolution_commit'];M=L['base_main']
commands=[];checks=[]
def run(cwd,*argv):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
    commands.append(dict(cwd=str(cwd),argv=list(argv),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode:raise RuntimeError(commands[-1])
    return p.stdout.strip()
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)));assert value,name
def api(*args):return json.loads(run(ROOT,'gh','api',*args))
def save(name,value):(ROOT/'artifacts'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def pr():
    for _ in range(4):
        value=api(END)
        if value['head']['sha']==R and value['mergeable'] is not None:return value
        time.sleep(1)
    return value

root_head=run(PROJECT,'git','rev-parse','HEAD')
check('actual strict build passed before publication',L['build_exit_code']==0 and L['build_warnings']==0)
check('resolution main clean',run(B,'git','status','--porcelain=v1','--untracked-files=all')=='')
check('local main is resolution merge',run(B,'git','rev-parse','HEAD')==R)
remote=run(B,'git','ls-remote','origin','refs/heads/main','refs/heads/docs/conflict-b')
refs={line.split()[1]:line.split()[0] for line in remote.splitlines()}
check('remote main still A merge',refs['refs/heads/main']==M)
check('remote B still original B commit',refs['refs/heads/docs/conflict-b']==L['b_original'])
run(B,'git','merge-base','--is-ancestor',L['b_original'],R)
run(B,'git','switch','docs/conflict-b')
run(B,'git','merge','--ff-only',R)
check('B branch fast-forward retains resolution history',run(B,'git','rev-parse','HEAD')==R)
run(B,'git','diff','--check',M+'...HEAD')
check('PR scope is five necessary files',set(run(B,'git','diff','--name-only',M+'...HEAD').splitlines())==set(L['files']))
run(B,'git','push','origin','docs/conflict-b')
body=f'''## Goal
Resolve the controlled conflict from the classroom exercise, actually build the documentation, and complete the B pull request.

## Changes
- Resolve `docs/build-check.md` to `{L['resolved_command'].strip()}`, retaining A's `-W` and B's `-n`.
- Remove all conflict markers and complete local merge commit `{R}` with parents `{M}` and `{L['b_original']}`.
- Add the minimum working Sphinx setup: `docs/conf.py`, `docs/index.md`, the existing course's hashed `requirements-docs.txt`, and ignores for `.venv`, `site`, and Python caches.
- The index includes the repository's current user/admin guides and the resolved command. Exactly five files differ from main.

## Validation
- Ran the exact resolved command in the repository root with isolated Python 3.13.12, Sphinx 8.2.3, and MyST 4.0.1.
- Build exit code 0, zero warnings with `-W -n`; HTML index generated and verified to contain the resolved command and current guides.
- Hashed dependency installation and `uv pip check` passed.
- `git diff --check` passed before staging; no unmerged index entries or MERGE_HEAD remain after the local merge.
- The local merge has both original parents. The source branch was advanced by a normal fast-forward push, preserving history.

## Limitations
This remains the user's authorized single-account automated role demonstration with `Zhi-Arman`; there is no independent student APPROVE review. The build validates this documentation only; application business tests and teacher acceptance are not claimed. All exercise branches must remain after merging.
'''
(ROOT/'artifacts/pr-body-final.md').write_text(body)
run(ROOT,'gh','pr','edit','3','--repo',REPO,'--title','docs: resolve build-check conflict and verify documentation build','--body-file',str(ROOT/'artifacts/pr-body-final.md'))
run(A,'git','fetch','--no-prune','origin')
check('A workspace clean for review',run(A,'git','status','--porcelain')=='')
check('review head matches published B',run(A,'git','rev-parse','origin/docs/conflict-b')==R)
run(A,'git','diff','--check','origin/main...origin/docs/conflict-b')
for name in L['files']:
    blob=run(A,'git','show',R+':'+name)
    check('reviewed source matches built '+name,blob==(B/name).read_text().strip())
check('A confirms both flags',run(A,'git','show',R+':docs/build-check.md')==L['resolved_command'].strip())
review=dict(event='COMMENT',commit_id=R,body=f'Automated A-role confirmation in the user-authorized single-account classroom demonstration. Reviewed exactly five necessary files at {R}. The resolution preserves both -W and -n, removes conflict markers, and retains both merge parents. The exact command built the current repository documentation with exit code 0 and zero warnings; published sources match the built files. This COMMENT is not independent student approval. Keep all exercise branches.')
save('review-request.json',review)
save('review-posted.json',api('--method','POST',END+'/reviews','--input',str(ROOT/'artifacts/review-request.json')))
before=pr();save('pr-before-merge.json',before)
check('B PR still open before merge',before['state']=='open')
check('PR head is built resolution commit',before['head']['sha']==R)
check('resolved PR is mergeable',before['mergeable'] is True)
check('GitHub PR contains exactly five changed files',before['changed_files']==5)
check('main did not advance during review',run(B,'git','ls-remote','origin','refs/heads/main').split()[0]==M)
payload=dict(sha=R,merge_method='merge',commit_title='Merge resolved build-check conflict and verified documentation',commit_message='Retain both -W and -n; actual strict documentation build passed. Authorized single-account classroom role demonstration; keep branches.')
save('merge-request.json',payload)
merged=api('--method','PUT',END+'/merge','--input',str(ROOT/'artifacts/merge-request.json'))
save('merge-response.json',merged)
check('GitHub merge succeeded',merged['merged'] is True)
final=api(END);save('pr-final.json',final)
F=merged['sha']
check('PR 3 marked merged',final['merged'] is True and final['state']=='closed')
workspaces={}
for role,path in [('A',A),('B',B)]:
    run(path,'git','fetch','--no-prune','origin')
    run(path,'git','switch','main')
    run(path,'git','pull','--ff-only','origin','main')
    check(role+' main matches final GitHub merge',run(path,'git','rev-parse','HEAD')==F)
    check(role+' worktree clean',run(path,'git','status','--porcelain=v1','--untracked-files=all')=='')
    check(role+' no unresolved index',run(path,'git','ls-files','--unmerged')=='')
    check(role+' no merge state',not (path/'.git/MERGE_HEAD').exists())
    run(path,'git','merge-base','--is-ancestor',L['b_original'],'main')
    run(path,'git','fsck','--full')
    workspaces[role]=dict(path=str(path),head=F,branch='main',status='CLEAN')
check('final GitHub merge parents verified',run(B,'git','rev-list','--parents','-n','1',F).split()==[F,M,R])
check('final tree equals actually built tree',run(B,'git','rev-parse',F+'^{tree}')==run(B,'git','rev-parse',R+'^{tree}'))
check('final command unchanged after PR merge',(B/L['file']).read_text()==L['resolved_command'])
check('no conflict markers in tracked docs',not re.search(r'^(<<<<<<<|=======|>>>>>>>)',(B/L['file']).read_text(),re.M))
allrefs=run(B,'git','ls-remote','origin','refs/heads/main','refs/heads/docs/preview','refs/heads/docs/conflict-base','refs/heads/docs/conflict-a','refs/heads/docs/conflict-b')
refs={line.split()[1]:line.split()[0] for line in allrefs.splitlines()}
for branch in ('docs/preview','docs/conflict-base','docs/conflict-a','docs/conflict-b'):
    check(branch+' retained','refs/heads/'+branch in refs)
check('B remote branch retains resolution',refs['refs/heads/docs/conflict-b']==R)
check('root StudySpace main preserved',run(PROJECT,'git','rev-parse','HEAD')==root_head)
check('root tracked contents preserved',run(PROJECT,'git','diff','HEAD','--')=='')
(ROOT/'artifacts/history-final.txt').write_text(run(B,'git','log','--graph','--oneline','--decorate','-14')+'\n')
comment=f'Conflict-resolution task completed by the authorized single-account automation. The exact -W -n command built the current documentation with exit code 0 and zero warnings before staging. Resolution merge {R} retains both original parents; PR merged at {F}. A/B main workspaces are clean and synchronized, no unmerged index or MERGE_HEAD remains, and all exercise branches are retained. Documentation build PASS; application business tests NOT_RUN; independent student execution NOT_VERIFIED.'
(ROOT/'artifacts/completion-comment.md').write_text(comment+'\n')
run(ROOT,'gh','pr','comment','3','--repo',REPO,'--body-file',str(ROOT/'artifacts/completion-comment.md'))
result=dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),status='CONFLICT_RESOLVED_BUILD_PASS_MERGED',
            pr_url=final['html_url'],pr_number=3,base_main=M,b_original=L['b_original'],resolution_commit=R,final_merge=F,
            resolved_command=L['resolved_command'],build_exit_code=L['build_exit_code'],build_warnings=L['build_warnings'],
            build_html=L['html'],build_versions=L['versions'],support_files=L['files'],workspaces=workspaces,
            branches_preserved=True,mode=L['mode'],independent_approval='NOT_VERIFIED',business_tests='NOT_RUN',
            local_checks=len(L['checks']),checks=checks,commands=commands)
save('execution.json',result)
print(json.dumps({k:result[k] for k in ('status','pr_url','resolution_commit','final_merge','build_exit_code','build_warnings')},ensure_ascii=False,indent=2))
print('Publication checks passed:',len(checks),'/',len(checks))
