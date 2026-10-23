from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import json

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
REPO = 'Zhi-Arman/studyspace-git-practice'
URL = 'https://github.com/'+REPO+'.git'
commands=[]
checks=[]
def run(cwd,*args,ok=True):
    p=subprocess.run(args,cwd=cwd,text=True,capture_output=True)
    commands.append(dict(cwd=str(cwd),argv=list(args),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if ok and p.returncode: raise RuntimeError(commands[-1])
    return p.stdout.strip()
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)))
    assert value,name

login=run(ROOT,'gh','api','user','--jq','.login')
repo=json.loads(run(ROOT,'gh','api','repos/'+REPO,'--jq','{full_name,html_url,private,default_branch,permissions,delete_branch_on_merge}'))
check('authenticated GitHub account matches owner',login=='Zhi-Arman')
check('online repository private',repo['private'] is True)
check('online default branch main',repo['default_branch']=='main')
check('owner read and push permission',repo['permissions']['pull'] and repo['permissions']['push'])
if repo['delete_branch_on_merge']:
    run(ROOT,'gh','api','--method','PATCH','repos/'+REPO,'-F','delete_branch_on_merge=false')
    repo=json.loads(run(ROOT,'gh','api','repos/'+REPO,'--jq','{full_name,html_url,private,default_branch,permissions,delete_branch_on_merge}'))
check('automatic branch deletion disabled',repo['delete_branch_on_merge'] is False)
expected=json.loads((ROOT/'artifacts/online-preparation.json').read_text())['head']
online_head=run(ROOT,'git','ls-remote',URL,'refs/heads/main').split()[0]
check('uploaded main matches prepared commit',online_head==expected)
repos={}
for label in ('author-a','author-b','reviewer'):
    path=ROOT/label
    if not path.exists():
        run(ROOT,'gh','repo','clone',REPO,str(path),'--','--branch','main')
    else:
        origin=run(path,'git','remote','get-url','origin')
        if origin!=URL:
            check(label+' clean before synchronization',run(path,'git','status','--porcelain=v1','--untracked-files=all')=='')
            run(path,'git','remote','rename','origin','teaching')
            run(path,'git','remote','add','origin',URL)
        run(path,'git','fetch','--no-prune','origin')
        run(path,'git','branch','--set-upstream-to=origin/main','main')
        run(path,'git','pull','--ff-only','origin','main')
    check(label+' online origin',run(path,'git','remote','get-url','origin')==URL)
    check(label+' main checked out',run(path,'git','branch','--show-current')=='main')
    head=run(path,'git','rev-parse','HEAD')
    check(label+' main matches online main',head==online_head)
    check(label+' fresh origin/main matches online main',run(path,'git','rev-parse','origin/main')==online_head)
    check(label+' no ahead or behind commits',run(path,'git','rev-list','--left-right','--count','main...origin/main').split()==['0','0'])
    check(label+' worktree and index clean',run(path,'git','status','--porcelain=v1','--untracked-files=all')=='')
    run(path,'git','fsck','--full')
    repos[label]=dict(path=str(path),origin=URL,head=head,status='CLEAN',ahead=0,behind=0)
check('online main unchanged after verification',run(ROOT,'git','ls-remote',URL,'refs/heads/main').split()[0]==online_head)
local=json.loads((ROOT/'artifacts/verification.json').read_text())
check('StudySpace root main preserved',run(PROJECT,'git','rev-parse','HEAD')==local['project']['head'])
check('StudySpace root tracked files unmodified',run(PROJECT,'git','diff','HEAD','--')=='')
protection_raw=run(ROOT,'gh','api','repos/'+REPO+'/branches/main/protection',ok=False)
protection_command=commands[-1]
result=dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
            status='ONLINE_OWNER_VERIFIED',login=login,repository=repo,online_main=online_head,
            repositories=repos,checks=checks,commands=commands,
            branch_protection='NOT_CONFIGURED' if protection_command['exit_code'] else 'CONFIGURED',
            collaborator_permissions='NOT_VERIFIED',human_execution='NOT_VERIFIED',business_tests='NOT_RUN',
            earlier_cli_auth_failure='Restricted network result superseded by successful escalated CLI authentication and repository access')
(ROOT/'artifacts/online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('status','repository','online_main','repositories','branch_protection')},ensure_ascii=False,indent=2))
print('Online checks passed:',sum(c['passed'] for c in checks),'/',len(checks))
