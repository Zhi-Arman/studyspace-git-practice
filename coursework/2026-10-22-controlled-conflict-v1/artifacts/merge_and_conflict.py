from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[1]
A=ROOT/'author-a';B=ROOT/'author-b'
P=json.loads((ROOT/'artifacts/preparation.json').read_text())
PRS=json.loads((ROOT/'artifacts/prs.json').read_text())
REPO=P['repository'];FILE=P['file']
commands=[];checks=[]
def run(cwd,*argv,ok=True):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
    commands.append(dict(cwd=str(cwd),argv=list(argv),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if ok and p.returncode:raise RuntimeError(commands[-1])
    return p.stdout.strip(),p.returncode
def out(cwd,*argv):return run(cwd,*argv)[0]
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)));assert value,name
def api(*args):return json.loads(out(ROOT,'gh','api',*args))
def save(name,value):(ROOT/'artifacts'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def get_pr(number):
    endpoint='repos/'+REPO+'/pulls/'+str(number)
    for attempt in range(3):
        pr=api(endpoint)
        if pr['mergeable'] is not None:return pr
        time.sleep(1)
    return pr

check('A and B independently start from same seed',out(A,'git','rev-parse',P['a_head']+'^')==P['common_base'] and out(B,'git','rev-parse',P['b_head']+'^')==P['common_base'])
for role,path,head in [('A',A,P['a_head']),('B',B,P['b_head'])]:
    check(role+' initial worktree clean',out(path,'git','status','--porcelain')=='')
    check(role+' single line changed against seed',out(path,'git','diff','--numstat',P['common_base'],head)=='1\t1\t'+FILE)
pra=get_pr(PRS['a_number']);save('pr-a-before.json',pra)
check('A PR exact head',pra['head']['sha']==P['a_head'])
check('A PR targets original main',pra['base']['sha']==P['original_main'])
check('A PR one exercise file only',pra['changed_files']==1)
check('A PR mergeable',pra['mergeable'] is True)
review=dict(event='COMMENT',commit_id=P['a_head'],body='Automated B-role check for the authorized single-account classroom demonstration. Verified that A and B have the same baseline parent, each changes only the one command line, and A adds -W. This COMMENT is not independent student approval. Merge A first; preserve all branches and the later B conflict. The Sphinx command was not executed.')
save('a-review-request.json',review)
save('a-review-posted.json',api('--method','POST','repos/'+REPO+'/pulls/'+str(PRS['a_number'])+'/reviews','--input',str(ROOT/'artifacts/a-review-request.json')))
payload=dict(sha=P['a_head'],merge_method='merge',commit_title='Merge controlled conflict A branch',commit_message='Merge A first in the authorized single-account classroom exercise. Keep all branches.')
save('a-merge-request.json',payload)
merge=api('--method','PUT','repos/'+REPO+'/pulls/'+str(PRS['a_number'])+'/merge','--input',str(ROOT/'artifacts/a-merge-request.json'))
save('a-merge-response.json',merge)
check('A merged first on GitHub',merge['merged'] is True)
main=merge['sha']
save('pr-a-final.json',api('repos/'+REPO+'/pulls/'+str(PRS['a_number'])))
out(A,'git','fetch','--no-prune','origin')
out(A,'git','switch','main')
out(A,'git','pull','--ff-only','origin','main')
check('A main clean and synchronized',out(A,'git','rev-parse','HEAD')==main and out(A,'git','status','--porcelain')=='')
check('main contains A command',out(A,'git','show','HEAD:'+FILE)+'\n'==P['a_command'])
out(B,'git','fetch','--no-prune','origin')
out(B,'git','switch','main')
out(B,'git','pull','--ff-only','origin','main')
check('B main synchronized before merge attempt',out(B,'git','rev-parse','HEAD')==main)
check('B clean before intentional merge',out(B,'git','status','--porcelain')=='')
merge_text,merge_code=run(B,'git','merge','--no-ff','--no-edit','docs/conflict-b',ok=False)
merge_command=commands[-1]
check('B merge attempt returns conflict exit code 1',merge_code==1)
check('B merge output reports content conflict','CONFLICT (content)' in merge_text and FILE in merge_text)
status=out(B,'git','status','--porcelain=v1')
check('only target file unmerged',status=='UU '+FILE)
unmerged=out(B,'git','ls-files','--unmerged','--',FILE)
stages=[int(line.split()[2]) for line in unmerged.splitlines()]
check('index retains all three merge stages',stages==[1,2,3])
blobs={str(i):out(B,'git','show',f':{i}:'+FILE)+'\n' for i in (1,2,3)}
check('stage 1 equals common baseline',blobs['1']==P['baseline_command'])
check('stage 2 equals A version on main',blobs['2']==P['a_command'])
check('stage 3 equals B branch version',blobs['3']==P['b_command'])
text=(B/FILE).read_text()
check('Git wrote real conflict markers','<<<<<<< HEAD\n' in text and '\n=======\n' in text and '\n>>>>>>> docs/conflict-b\n' in text)
check('B HEAD remains merged A main',out(B,'git','rev-parse','HEAD')==main)
check('B MERGE_HEAD identifies B branch',out(B,'git','rev-parse','MERGE_HEAD')==P['b_head'])
check('B merge-base is the shared seed',out(B,'git','merge-base','HEAD','MERGE_HEAD')==P['common_base'])
(ROOT/'artifacts/conflict-file.txt').write_text(text)
(ROOT/'artifacts/merge-output.txt').write_text(merge_command['stdout']+merge_command['stderr'])
(ROOT/'artifacts/status-conflict.txt').write_text(out(B,'git','status')+'\n')
(ROOT/'artifacts/index-stages.txt').write_text(unmerged+'\n')
(ROOT/'artifacts/conflict.diff').write_text(out(B,'git','diff','--cc','--',FILE)+'\n')
for key,value in blobs.items():(ROOT/f'artifacts/stage-{key}.txt').write_text(value)
prb=get_pr(PRS['b_number']);save('pr-b-conflict.json',prb)
check('B PR remains open',prb['state']=='open' and prb['merged'] is False)
check('B PR exact B head preserved',prb['head']['sha']==P['b_head'])
check('GitHub detects B PR conflict',prb['mergeable'] is False and prb['mergeable_state']=='dirty')
comment=f'''Controlled conflict reproduced by automation in the authorized single-account classroom exercise.

A PR #{PRS['a_number']} merged first at `{main}`. Both branches start from `{P['common_base']}` and each changes only the single line in `{FILE}`.

In the isolated B workspace, `git merge --no-ff --no-edit docs/conflict-b` from the updated `main` returned exit code 1 and a content conflict. `git status --porcelain=v1` reports `UU {FILE}`. The index contains stages 1 (baseline), 2 (A/main), and 3 (B); MERGE_HEAD is `{P['b_head']}`. GitHub also reports this PR as conflicting.

This task ends at the conflict. B PR stays open, the B workspace stays in the unresolved merge state, and no resolution or merge abort was performed. Keep all branches. Sphinx build execution and business tests are NOT_RUN. This is not proof of the students' personal execution.'''
(ROOT/'artifacts/b-conflict-comment.md').write_text(comment)
out(ROOT,'gh','pr','comment',str(PRS['b_number']),'--repo',REPO,'--body-file',str(ROOT/'artifacts/b-conflict-comment.md'))
refs_raw=out(A,'git','ls-remote','origin','refs/heads/main','refs/heads/docs/preview','refs/heads/docs/conflict-base','refs/heads/docs/conflict-a','refs/heads/docs/conflict-b')
refs={line.split()[1]:line.split()[0] for line in refs_raw.splitlines()}
check('remote main remains A merge',refs.get('refs/heads/main')==main)
for branch,head in [('docs/conflict-base',P['common_base']),('docs/conflict-a',P['a_head']),('docs/conflict-b',P['b_head'])]:
    check(branch+' preserved',refs.get('refs/heads/'+branch)==head)
check('previous docs/preview retained','refs/heads/docs/preview' in refs)
check('existing shared documents preserved',all(hashlib.sha256((A/n).read_bytes()).hexdigest()==h for n,h in P['source_hashes'].items()))
check('StudySpace root main unchanged',out(PROJECT,'git','rev-parse','HEAD')==P['root_project_head'])
check('StudySpace tracked files unchanged',out(PROJECT,'git','diff','HEAD','--')=='')
check('B conflict still present at completion',out(B,'git','status','--porcelain=v1')=='UU '+FILE and out(B,'git','rev-parse','MERGE_HEAD')==P['b_head'])
for path in (A,B):out(path,'git','fsck','--full')
result=dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),status='EXPECTED_CONFLICT_PRESERVED',
            mode=P['mode'],actor=P['actor'],file=FILE,original_main=P['original_main'],common_base=P['common_base'],
            a_head=P['a_head'],b_head=P['b_head'],a_merge_commit=main,a_pr_url=PRS['a_url'],b_pr_url=PRS['b_url'],
            a_pr_number=PRS['a_number'],b_pr_number=PRS['b_number'],
            a_workspace=str(A),b_workspace=str(B),conflict_file=str(B/FILE),
            commands_text=dict(baseline=P['baseline_command'],A=P['a_command'],B=P['b_command']),
            merge_exit_code=merge_code,merge_output=merge_command['stdout']+merge_command['stderr'],
            conflict_text=text,status_porcelain=status,merge_head=P['b_head'],stages=blobs,
            checks=checks,commands=commands,refs=refs,branches_preserved=True,
            conflict_resolution='NOT_RUN',merge_abort='NOT_RUN',build_execution='NOT_RUN',business_tests='NOT_RUN',human_execution='NOT_VERIFIED')
save('execution.json',result)
print(json.dumps({k:result[k] for k in ('status','a_pr_url','b_pr_url','a_merge_commit','common_base','merge_exit_code','status_porcelain','conflict_file')},ensure_ascii=False,indent=2))
print('Final checks passed:',len(checks),'/',len(checks))
