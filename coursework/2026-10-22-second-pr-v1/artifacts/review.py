from workflow import *

P = json.loads((ART / 'pr-created.json').read_text())
I = json.loads((ART / 'initial.json').read_text())
pr = gh([f'repos/{REPO}/pulls/{P["number"]}'])
assert pr['state'] == 'open' and pr['head']['sha'] == I['head']
assert (B / 'docs/build-check.md').read_text() == COMMAND + '\n'
assert run(['git', 'ls-files', '-u']) == ''
assert run(['git', 'grep', '-n', '-E', '^(<{7}|={7}|>{7})( |$)', '--', '*.md'], allowed=(1,)) == ''
run(['git', 'diff', '--check', BASE, I['head']])
run(['git', 'merge-base', '--is-ancestor', RESOLUTION, I['head']])
save('review-checks.json', dict(head=I['head'], resolved_command_correct=True,
     no_tracked_markdown_markers=True, bilingual_conflict_record_correct=True,
     finding='The new pre-commit instructions omit an explicit tracked-file marker scan and its exit-code interpretation. A clean working diff does not inspect existing committed content.'))
body = {
    'event': 'COMMENT', 'commit_id': I['head'],
    'body': 'Automated reviewer-role demonstration, actually performed by Zhi-Arman; not an independent student approval. Checked the combined -W -n command, bilingual conflict explanation, empty unmerged index, and tracked Markdown marker scan. These checks pass. One concrete documentation correction is requested below before confirmation.',
    'comments': [{
        'path': 'docs/index.md', 'line': I['line'], 'side': 'RIGHT',
        'body': 'Please add a reproducible scan of tracked Markdown for conflict-marker lines and explain its exit codes (1 = no matches, 0 = markers found, greater than 1 = execution error). The listed diff/index checks are useful, but a clean working diff does not scan already committed content. Keep the explanation paired in Chinese and Russian.'
    }]
}
save('review-request.json', body)
response = gh(['--method', 'POST', f'repos/{REPO}/pulls/{P["number"]}/reviews', '--input', str(ART / 'review-request.json')])
save('review-posted.json', response)
save('review-comments.json', gh([f'repos/{REPO}/pulls/{P["number"]}/comments']))
print(response['html_url'])
