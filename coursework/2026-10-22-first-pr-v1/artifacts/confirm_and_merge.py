from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
REPO='Zhi-Arman/studyspace-git-practice'
ENDPOINT='repos/'+REPO+'/pulls/1'
commands=[]
checks=[]
def run(cwd,*argv):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
    commands.append(dict(cwd=str(cwd),argv=list(argv),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode:raise RuntimeError(commands[-1])
    return p.stdout.strip()
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)))
    assert value,name
def api(*args):return json.loads(run(ROOT,'gh','api',*args))
def save(name,data):
    (ROOT/'artifacts'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

S=json.loads((ROOT/'artifacts/start.json').read_text())
C=json.loads((ROOT/'artifacts/correction.json').read_text())
head=C['corrected_head']
root_head=run(PROJECT,'git','rev-parse','HEAD')
assert S['mode']=='SINGLE_ACCOUNT_AUTOMATED_ROLE_DEMO'
author_response=run(ROOT,'gh','pr','comment','1','--repo',REPO,'--body-file',str(ROOT/'artifacts/author-response.md'))
confirmation=api('--method','POST',ENDPOINT+'/reviews','--input',str(ROOT/'artifacts/confirmation-request.json'))
save('confirmation-posted.json',confirmation)
check('B-role confirmation is COMMENTED not impersonated approval',confirmation['state']=='COMMENTED')
check('B-role confirmation anchored to corrected head',confirmation['commit_id']==head)
query='query { repository(owner:"Zhi-Arman", name:"studyspace-git-practice") { pullRequest(number:1) { reviewThreads(first:20) { nodes { id isResolved comments(first:5) { nodes { body url author { login } } } } } } } }'
threads=api('graphql','-f','query='+query)
save('review-threads-before.json',threads)
nodes=threads['data']['repository']['pullRequest']['reviewThreads']['nodes']
check('one concrete inline review thread',len(nodes)==1)
for node in nodes:
    if not node['isResolved']:
        result=api('graphql','-f','query=mutation($threadId:ID!){resolveReviewThread(input:{threadId:$threadId}){thread{id isResolved}}}','-f','threadId='+node['id'])
        save('review-thread-resolution.json',result)
        check('concrete review thread resolved',result['data']['resolveReviewThread']['thread']['isResolved'])

body=f'''## Goal
Complete the first pull request exercise with a small user-guide clarification on `docs/preview`.

## Changes
- Replace the old direct `main` push example with `git push -u origin docs/preview`.
- Address the review finding by checking `git branch --show-current` before staging and committing. Both Chinese and Russian instructions require `docs/preview` and stopping on a mismatch.
- The final diff changes only `user-guide.md`.

## Validation
- Branch started from freshly synchronized `main` at `{S['base']}`.
- Initial change: `{S['initial_head']}`; review correction: `{head}`.
- `git diff --check` passed for the correction and full PR diff.
- The separate B workspace fetched the corrected commit, reported `docs/preview`, matched the remote head, and had a clean worktree.
- The concrete inline review thread was addressed and resolved; the B-role automated COMMENT confirmation is anchored to `{head}`.

## Limitations
This is a single-account automated classroom role demonstration explicitly authorized by the user. A and B actions use `Zhi-Arman`; they are not evidence of the named students' personal execution. Review and confirmation use COMMENT, not an independent APPROVE review. VS Code visual preview and business tests were not run. The source branch must remain after merging.
'''
(ROOT/'artifacts/pr-body-final.md').write_text(body)
run(ROOT,'gh','pr','edit','1','--repo',REPO,'--body-file',str(ROOT/'artifacts/pr-body-final.md'))
pr=api(ENDPOINT)
save('pr-before-merge.json',pr)
check('PR open before merge',pr['state']=='open')
check('PR head matches reviewed correction',pr['head']['sha']==head)
check('PR base remains original main',pr['base']['sha']==S['base'])
check('PR changes one file',pr['changed_files']==1)
check('PR is mergeable',pr['mergeable'] is True)
reviews=api(ENDPOINT+'/reviews')
save('reviews-before-merge.json',reviews)
check('initial review and correction confirmation both present',len(reviews)==2)
check('all reviews transparently COMMENTED',all(x['state']=='COMMENTED' for x in reviews))
check('initial review anchors initial commit',reviews[0]['commit_id']==S['initial_head'])
check('confirmation anchors final commit',reviews[1]['commit_id']==head)
payload=dict(sha=head,merge_method='merge',commit_title='Merge pull request #1 from docs/preview',
             commit_message='Complete authorized single-account classroom role demonstration; retain docs/preview.')
save('merge-request.json',payload)
merge=api('--method','PUT',ENDPOINT+'/merge','--input',str(ROOT/'artifacts/merge-request.json'))
save('merge-response.json',merge)
check('GitHub confirms merge',merge['merged'] is True)
after=api(ENDPOINT)
save('pr-final.json',after)
check('PR marked merged',after['merged'] is True and after['state']=='closed')
check('merge commit matches GitHub response',after['merge_commit_sha']==merge['sha'])
remote=run(ROOT,'git','ls-remote','https://github.com/'+REPO+'.git','refs/heads/main','refs/heads/docs/preview')
refs={line.split()[1]:line.split()[0] for line in remote.splitlines()}
check('source branch preserved on GitHub',refs.get('refs/heads/docs/preview')==head)
check('GitHub main is merge commit',refs.get('refs/heads/main')==merge['sha'])
workspaces={}
for role in ('author-a','reviewer-b'):
    path=ROOT/role
    run(path,'git','fetch','--no-prune','origin')
    run(path,'git','switch','main')
    run(path,'git','pull','--ff-only','origin','main')
    check(role+' main matches merged main',run(path,'git','rev-parse','HEAD')==merge['sha'])
    check(role+' clean worktree',run(path,'git','status','--porcelain=v1','--untracked-files=all')=='')
    check(role+' local preview branch preserved',run(path,'git','rev-parse','docs/preview')==head)
    run(path,'git','merge-base','--is-ancestor',head,'main')
    run(path,'git','fsck','--full')
    workspaces[role]=dict(path=str(path),branch='main',head=merge['sha'],status='CLEAN',preserved_preview=head)
check('StudySpace root commit unchanged',run(PROJECT,'git','rev-parse','HEAD')==root_head)
check('StudySpace tracked files unchanged',run(PROJECT,'git','diff','HEAD','--')=='')
resolved=api('graphql','-f','query='+query)
save('review-threads-final.json',resolved)
check('review thread remains resolved',all(n['isResolved'] for n in resolved['data']['repository']['pullRequest']['reviewThreads']['nodes']))
result=dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),mode=S['mode'],
            pr_url=after['html_url'],pr_number=1,repository=REPO,base=S['base'],
            initial_head=S['initial_head'],corrected_head=head,merge_commit=merge['sha'],
            merged=True,branch_preserved=True,workspaces=workspaces,checks=checks,commands=commands,
            actual_actor='Zhi-Arman',independent_approval='NOT_VERIFIED',review_event='COMMENT',
            role_A='支浩然',role_B='俞智文',role_rotation='B acts as reviewer for this task per image',
            business_tests='NOT_RUN',vscode_visual_preview='NOT_RUN',
            author_response_url=author_response,initial_review_url=json.loads((ROOT/'artifacts/review-posted.json').read_text())['html_url'],confirmation_url=confirmation['html_url'])
save('execution.json',result)
print(json.dumps({k:result[k] for k in ('pr_url','merged','merge_commit','corrected_head','branch_preserved','independent_approval')},ensure_ascii=False,indent=2))
print('Final checks passed:',sum(x['passed'] for x in checks),'/',len(checks))
