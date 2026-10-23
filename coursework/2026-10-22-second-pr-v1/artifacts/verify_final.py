from workflow import *

M = json.loads((ART / 'merged.json').read_text())
I = json.loads((ART / 'initial.json').read_text())
C = json.loads((ART / 'correction.json').read_text())
R = json.loads((ART / 'review-posted.json').read_text())
F = json.loads((ART / 'confirmation-posted.json').read_text())
checks = []
def check(name, passed):
    checks.append(dict(name=name, passed=bool(passed)))
    assert passed, name

pr = gh([f'repos/{REPO}/pulls/{M["number"]}'])
reviews = gh([f'repos/{REPO}/pulls/{M["number"]}/reviews'])
comments = gh([f'repos/{REPO}/pulls/{M["number"]}/comments'])
save('reviews-final.json', reviews)
save('comments-final.json', comments)
save('pr-final.json', pr)
check('PR merged', pr['merged'] is True and pr['state'] == 'closed')
check('PR target main', pr['base']['ref'] == 'main')
check('PR head original resolved branch', pr['head']['ref'] == 'docs/conflict-b')
check('Merged corrected head', pr['head']['sha'] == C['head'])
check('Expected merge hash', pr['merge_commit_sha'] == M['merge'])
check('Two COMMENT reviews', len(reviews) == 2 and all(x['state'] == 'COMMENTED' for x in reviews))
check('Review on initial head', R['commit_id'] == I['head'])
check('Confirmation on corrected head', F['commit_id'] == C['head'])
check('One concrete inline comment', len(comments) == 1 and comments[0]['path'] == 'docs/index.md')
check('Review preceded confirmation', R['submitted_at'] <= F['submitted_at'])
check('Confirmation before merge', F['submitted_at'] <= pr['merged_at'])
check('Actual account disclosed', all(x['user']['login'] == 'Zhi-Arman' and 'Automated' in x['body'] for x in reviews))
resolved = json.loads((ART / 'review-thread-resolved.json').read_text())
check('Review thread resolved', resolved['data']['resolveReviewThread']['thread']['isResolved'])
check('One correction commit', run(['git','rev-list','--count', I['head']+'..'+C['head']]) == '1')
check('Correction parent matches review head', run(['git','rev-parse', C['head']+'^']) == I['head'])
check('Correction touches only docs index', run(['git','diff','--name-only',I['head'],C['head']]) == 'docs/index.md')
check('PR diff touches only docs index', run(['git','diff','--name-only',BASE,C['head']]) == 'docs/index.md')
check('Resolution preserved in history', run(['git','merge-base','--is-ancestor',RESOLUTION,C['head']]) == '')
check('Two merge parents preserve base and corrected head', run(['git','show','-s','--format=%P',M['merge']]).split() == [BASE,C['head']])
check('Merged tree equals actually built corrected tree', run(['git','rev-parse',M['merge']+'^{tree}']) == run(['git','rev-parse',C['head']+'^{tree}']))
check('Exact final command retained', (B/'docs/build-check.md').read_text() == COMMAND+'\n')
check('Marker scan clean', run(['git','grep','-n','-E','^(<{7}|={7}|>{7})( |$)','--','*.md'],allowed=(1,)) == '')
check('Full PR diff check clean', run(['git','diff','--check',BASE,M['merge']]) == '')
for label in ('initial','corrected'):
    v = json.loads((ART/(label+'-validation.json')).read_text())
    log = (ART/(label+'-sphinx-build.log')).read_text()
    check(label+' actual build passed with zero warnings', v['build_exit_code'] == 0 and v['warnings'] == 0 and 'build succeeded.' in log and 'WARNING:' not in log)
check('Generated HTML exists', (B/'site/index.html').is_file())
workspaces = {}
for name,work in [('A',A),('B',B)]:
    state = dict(path=str(work),branch=run(['git','branch','--show-current'],cwd=work),
                 head=run(['git','rev-parse','HEAD'],cwd=work),
                 status=run(['git','status','--porcelain=v1','--untracked-files=all'],cwd=work),
                 unmerged=run(['git','ls-files','-u'],cwd=work),
                 merge_head=(work/'.git/MERGE_HEAD').exists())
    workspaces[name]=state
    check(name+' on synchronized clean main',state['branch']=='main' and state['head']==M['merge'] and state['status']=='')
    check(name+' no pending merge',state['unmerged']=='' and not state['merge_head'])
refs = run(['git','ls-remote','origin','refs/heads/*'])
remote = {line.split()[1].removeprefix('refs/heads/'):line.split()[0] for line in refs.splitlines()}
check('Online main matches final merge',remote.get('main')==M['merge'])
check('B branch retains correction',remote.get('docs/conflict-b')==C['head'])
check('Other exercise branches retained',all(remote.get(k)==v for k,v in {
    'docs/preview':'438984ac3a265512fbd0dff6471ce03797a152db',
    'docs/conflict-base':'569a94ac86983d1180866f65126eee6d5efad6c0',
    'docs/conflict-a':'252c62879b5237571545756b477333a2450064d8'}.items()))
repo = gh([f'repos/{REPO}'])
check('Automatic branch deletion disabled',repo['delete_branch_on_merge'] is False)
history=run(['git','log','--graph','--oneline','--decorate','--all','-22'])
(ART/'history-final.txt').write_text(history+'\n')
text=(B/'docs/index.md').read_text()
check('Correction present in Chinese and Russian', '返回 1 表示无匹配' in text and 'код 1 означает отсутствие совпадений' in text)
check('Explicit marker scan and command errors documented', "git grep -n -E '^(<{7}|={7}|>{7})( |$)' -- '*.md'" in text and 'код больше 1' in text)
check('Primary StudySpace tracked files clean',run(['git','status','--porcelain=v1','--untracked-files=no'],cwd=ROOT.parents[1])=='')
result=dict(status='SECOND_PR_REVIEW_CORRECT_CONFIRM_MERGED',executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
    pr_url=M['pr_url'],pr_number=M['number'],base=BASE,resolution=RESOLUTION,initial=I['head'],corrected=C['head'],merge=M['merge'],
    review_url=R['html_url'],confirmation_url=F['html_url'],review_comment_url=comments[0]['html_url'],
    review_kind='COMMENT',independent_approval='NOT_VERIFIED',business_tests='NOT_RUN',
    single_account_automated_role_demonstration=True,prior_resolution_pr=3,workspaces=workspaces,
    remote_branches=remote,build_command=COMMAND,build_exit_code=0,warnings=0,checks=checks)
save('execution.json',result)
print(json.dumps(dict(status=result['status'],checks=len(checks),merged=M['merge']),ensure_ascii=False))
