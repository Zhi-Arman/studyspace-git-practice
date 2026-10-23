from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
WORK=ROOT/'author-a'
REPO='Zhi-Arman/studyspace-git-practice'
commands=[]
def run(cwd,*argv):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
    commands.append(dict(cwd=str(cwd),argv=list(argv),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode:raise RuntimeError(commands[-1])
    return p.stdout.strip()

if not WORK.exists():run(ROOT,'gh','repo','clone',REPO,str(WORK),'--','--branch','main')
assert run(WORK,'git','status','--porcelain=v1','--untracked-files=all')==''
run(WORK,'git','fetch','--no-prune','origin')
run(WORK,'git','pull','--ff-only','origin','main')
base=run(WORK,'git','rev-parse','HEAD')
assert base==run(WORK,'git','ls-remote','origin','refs/heads/main').split()[0]
for key in ('user.name','user.email'):
    value=subprocess.check_output(['git','config','--local','--get',key],cwd=PROJECT,text=True).strip()
    subprocess.run(['git','config','--local',key,value],cwd=WORK,check=True)
run(WORK,'git','switch','-c','docs/preview')
guide=WORK/'user-guide.md'
before=guide.read_text()
assert before.count('git push origin main')==1
guide.write_text(before.replace('git push origin main','git push -u origin docs/preview'))
run(WORK,'git','diff','--check')
assert run(WORK,'git','diff','--name-only')=='user-guide.md'
(ROOT/'artifacts/initial.diff').write_text(run(WORK,'git','diff','--','user-guide.md')+'\n')
run(WORK,'git','add','--','user-guide.md')
run(WORK,'git','commit','-m','docs: publish user guide changes from preview branch')
head=run(WORK,'git','rev-parse','HEAD')
run(WORK,'git','push','-u','origin','docs/preview')
assert run(WORK,'git','ls-remote','origin','refs/heads/docs/preview').split()[0]==head
assert run(WORK,'git','status','--porcelain=v1','--untracked-files=all')==''
shutil.copy2('/var/folders/ff/kqw394c93dd7krl0z2hcqqdh0000gn/T/codex-clipboard-3d1ce701-0113-4f32-93b1-64cface4a6e6.jpg',ROOT/'artifacts/task.jpg')
result=dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),repository=REPO,
            base=base,initial_head=head,branch='docs/preview',commands=commands,
            mode='SINGLE_ACCOUNT_AUTOMATED_ROLE_DEMO',actual_account='Zhi-Arman',
            user_authorization='按单账号课堂演示完成确认和合并，明确标记为自动化角色演示',
            role_A='支浩然',role_B='俞智文',independent_B_approval='NOT_VERIFIED',business_tests='NOT_RUN')
(ROOT/'artifacts/start.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(base=base,initial_head=head,branch='docs/preview',diff=(ROOT/'artifacts/initial.diff').read_text()),ensure_ascii=False,indent=2))
