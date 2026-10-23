from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'author-a'
B=ROOT/'reviewer-b'
commands=[]
def run(cwd,*argv):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
    commands.append(dict(cwd=str(cwd),argv=list(argv),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode:raise RuntimeError(commands[-1])
    return p.stdout.strip()
review=json.loads((ROOT/'artifacts/review-posted.json').read_text())
assert review['state']=='COMMENTED'
assert run(A,'git','branch','--show-current')=='docs/preview'
assert run(A,'git','status','--porcelain')==''
path=A/'user-guide.md'
source=path.read_text()
old='```bash\ngit add user-guide.md'
new='''先执行 git branch --show-current，预期输出为 docs/preview；若不是该分支，停止后续命令并先切换到正确分支。确认后再暂存、提交和推送。

Сначала выполните git branch --show-current; ожидается docs/preview. Если выбрана другая ветка, остановитесь и перейдите в нужную ветку. Только затем добавляйте файл, создавайте коммит и отправляйте изменения.

```bash
git branch --show-current
git add user-guide.md'''
assert source.count(old)==1
path.write_text(source.replace(old,new))
run(A,'git','diff','--check')
assert run(A,'git','diff','--name-only')=='user-guide.md'
(ROOT/'artifacts/correction.diff').write_text(run(A,'git','diff','--','user-guide.md')+'\n')
run(A,'git','add','--','user-guide.md')
run(A,'git','commit','-m','docs: check preview branch before committing guide changes')
head=run(A,'git','rev-parse','HEAD')
run(A,'git','push','origin','docs/preview')
run(B,'git','fetch','--no-prune','origin')
run(B,'git','pull','--ff-only','origin','docs/preview')
assert run(B,'git','rev-parse','HEAD')==head
assert run(B,'git','branch','--show-current')=='docs/preview'
run(B,'git','diff','--check','origin/main...HEAD')
assert run(B,'git','diff','--name-only','origin/main...HEAD')=='user-guide.md'
text=(B/'user-guide.md').read_text()
assert '若不是该分支，停止后续命令' in text
assert 'Если выбрана другая ветка, остановитесь' in text
assert '```bash\ngit branch --show-current\ngit add user-guide.md' in text
assert 'git push -u origin docs/preview' in text
assert 'git push origin main' not in text
assert run(A,'git','status','--porcelain')==''
assert run(B,'git','status','--porcelain')==''
(ROOT/'artifacts/final.diff').write_text(run(B,'git','diff','origin/main...HEAD','--','user-guide.md')+'\n')
confirmation=f'''B-role automated confirmation (single-account classroom demonstration).

Verified correction commit `{head}` in the separate B workspace. The guide now checks `git branch --show-current` before staging, gives the expected `docs/preview` output, and tells the reader to stop on a mismatch in both Chinese and Russian. `git diff --check` passes; the PR still changes only `user-guide.md`; the B workspace is clean and matches the published branch.

The concrete review finding is addressed. The owner may merge this authorized classroom demonstration and retain the branch. This COMMENT is not an independent GitHub APPROVE review or evidence of a student's personal execution. VS Code visual preview and business tests were not run.'''
(ROOT/'artifacts/confirmation-request.json').write_text(json.dumps(dict(commit_id=head,event='COMMENT',body=confirmation),ensure_ascii=False,indent=2)+'\n')
(ROOT/'artifacts/author-response.md').write_text(f'A-role automated response (single-account classroom demonstration): addressed the branch-check finding in `{head}`. Both languages state the expected branch and require stopping on a mismatch. The new check runs before staging and committing.\n')
result=dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),corrected_head=head,commands=commands,
            checks=dict(diff_check='PASS',one_file_only=True,branch_output='docs/preview',chinese_stop_rule=True,russian_stop_rule=True,clean_A=True,clean_B=True),
            review_finding='ADD_CURRENT_BRANCH_CHECK',finding_status='ADDRESSED',independent_approval='NOT_VERIFIED')
(ROOT/'artifacts/correction.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result['checks']|dict(corrected_head=head),ensure_ascii=False,indent=2))
