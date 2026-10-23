from workflow import *
import time

P = json.loads((ART / 'pr-created.json').read_text())
I = json.loads((ART / 'initial.json').read_text())
C = json.loads((ART / 'correction.json').read_text())
assert run(['git', 'rev-parse', 'HEAD']) == C['head']
assert run(['git', 'status', '--porcelain=v1']) == ''
run(['git', 'push', 'origin', 'docs/conflict-b'])
for attempt in range(5):
    pr = gh([f'repos/{REPO}/pulls/{P["number"]}'])
    if pr['head']['sha'] == C['head']: break
    time.sleep(1)
assert pr['head']['sha'] == C['head'] and pr['state'] == 'open'
files = gh([f'repos/{REPO}/pulls/{P["number"]}/files'])
assert [f['filename'] for f in files] == ['docs/index.md']
run(['git', 'diff', '--check', BASE, C['head']])
assert run(['git', 'grep', '-n', '-E', '^(<{7}|={7}|>{7})( |$)', '--', '*.md'], allowed=(1,)) == ''
assert run(['git', 'ls-files', '-u']) == ''
assert (B / 'docs/build-check.md').read_text() == COMMAND + '\n'
assert 'код больше 1' in (B / 'docs/index.md').read_text()
save('pr-files-before-merge.json', files)

body = (ART / 'pr-body-initial.md').read_text()
body += f'''\n## Review correction and confirmation
- Initial review head: `{I['head']}`.
- Automated reviewer checked marker absence and bilingual wording, then requested one explicit tracked-Markdown marker scan with exit-code interpretation.
- One correction commit: `{C['head']}`. It changes only `docs/index.md` and adds the scan plus paired Chinese/Russian explanations: 1 = no matches, 0 = markers found, greater than 1 = execution error.
- Reran diff/index/marker checks and the exact real Sphinx build: exit 0, zero warnings.
- Confirmation is recorded as a separate automated reviewer-role COMMENT tied to the corrected head, not as an independent GitHub APPROVE.
'''
(ART / 'pr-body-final.md').write_text(body)
run(['gh', 'pr', 'edit', str(P['number']), '--repo', REPO, '--body-file', str(ART / 'pr-body-final.md')])
confirmation = dict(event='COMMENT', commit_id=C['head'], body=f'''Automated reviewer-role confirmation (actual account: Zhi-Arman; not independent APPROVE).
Checked correction commit {C['head']}: the requested tracked-Markdown marker scan and correct exit-code interpretation are present in both Chinese and Russian. No marker matches; unmerged index empty; diff check passed. The resolved command still preserves -W -n. The exact documentation build passed again with exit 0 and zero warnings. The one requested correction is addressed. Confirmed for merge for the user-authorized classroom demonstration; real student approval remains NOT_VERIFIED and application business tests remain NOT_RUN.''')
save('confirmation-request.json', confirmation)
save('confirmation-posted.json', gh(['--method', 'POST', f'repos/{REPO}/pulls/{P["number"]}/reviews', '--input', str(ART / 'confirmation-request.json')]))

query = 'query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){pullRequest(number:$number){reviewThreads(first:100){nodes{id isResolved comments(first:20){nodes{body url}}}}}}}'
threads = gh(['graphql','-f','query='+query,'-f','owner=Zhi-Arman','-f','name=studyspace-git-practice','-F','number='+str(P['number'])])
save('review-threads-before.json', threads)
nodes = threads['data']['repository']['pullRequest']['reviewThreads']['nodes']
assert len(nodes) == 1
mutation = 'mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{id isResolved}}}'
result = gh(['graphql','-f','query='+mutation,'-f','id='+nodes[0]['id']])
assert result['data']['resolveReviewThread']['thread']['isResolved']
save('review-thread-resolved.json', result)

for attempt in range(4):
    pr = gh([f'repos/{REPO}/pulls/{P["number"]}'])
    if pr['mergeable'] is not None: break
    time.sleep(1)
assert pr['mergeable'] is True and pr['head']['sha'] == C['head']
remote_main = run(['git', 'ls-remote', 'origin', 'refs/heads/main']).split()[0]
assert remote_main == BASE
save('pr-before-merge.json', pr)
payload = dict(sha=C['head'], merge_method='merge',
               commit_title='Merge second PR after automated review correction',
               commit_message='User-authorized single-account classroom demonstration: one review finding, one correction, verified build, COMMENT confirmation. No independent approval asserted; branches retained.')
save('merge-request.json', payload)
merged = gh(['--method', 'PUT', f'repos/{REPO}/pulls/{P["number"]}/merge', '--input', str(ART / 'merge-request.json')])
save('merge-response.json', merged)
assert merged['merged']
save('pr-final.json', gh([f'repos/{REPO}/pulls/{P["number"]}']))
for work in (A, B):
    run(['git', 'fetch', 'origin'], cwd=work)
    assert run(['git', 'status', '--porcelain=v1'], cwd=work) == ''
    run(['git', 'switch', 'main'], cwd=work)
    run(['git', 'pull', '--ff-only', 'origin', 'main'], cwd=work)
    assert run(['git', 'rev-parse', 'HEAD'], cwd=work) == merged['sha']
    assert run(['git', 'status', '--porcelain=v1'], cwd=work) == ''
save('merged.json', dict(pr_url=P['url'], number=P['number'], initial=I['head'], corrected=C['head'], merge=merged['sha']))
print(json.dumps(dict(url=P['url'], merged=merged['sha']), ensure_ascii=False))
