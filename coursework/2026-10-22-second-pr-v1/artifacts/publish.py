from workflow import *

I = json.loads((ART / 'initial.json').read_text())
assert run(['git', 'rev-parse', 'HEAD']) == I['head']
assert run(['git', 'status', '--porcelain=v1']) == ''
assert run(['gh', 'api', 'user', '--jq', '.login']) == 'Zhi-Arman'
run(['git', 'push', 'origin', 'docs/conflict-b'])
body = '''## Change
Continue classroom task 5 on the retained resolved-conflict branch `docs/conflict-b`.
PR #3 already published and merged the actual conflict resolution during task 4; this new PR records a separate review-and-correction cycle without rewriting that history.

### Conflict and selected solution
A and B changed the same single line in `docs/build-check.md` from one baseline: A added `-W`, B added `-n`. A merged first and B encountered a real conflict. Resolution commit `49de18441048777347d9c008e5ba4fe3149be977` preserved both flags:
`.venv/bin/python -m sphinx -W -n -b html docs site`

This PR adds a paired Chinese/Russian conflict-resolution record to `docs/index.md`; the resolved command and build configuration remain intact. The resolution commit is an ancestor of this branch.

## Validation
- `git diff --check`: passed.
- `git ls-files -u`: empty.
- Tracked Markdown conflict-marker scan: no matches (expected exit 1).
- `uv pip check` using the existing isolated environment: passed.
- Actual Sphinx build with the exact combined command: exit 0, zero warnings.
- Current user/admin guides and the conflict record are included in generated HTML.

## Reviewer
User-authorized single-account automated classroom role demonstration. B is the author role; Cao Haoran (曹浩然) is the reviewer role only. All GitHub actions are actually performed by `Zhi-Arman`. Review and confirmation use COMMENT, not independent APPROVE. No student's personal execution, agreement, or approval is asserted.

## Limitations
Documentation and Git exercise only; application business tests remain NOT_RUN. All exercise branches will be retained; no force push or branch deletion.
'''
(ART / 'pr-body-initial.md').write_text(body)
url = run(['gh', 'pr', 'create', '--repo', REPO, '--base', 'main', '--head', 'docs/conflict-b',
           '--title', 'docs: review resolved build-check conflict in second pull request',
           '--body-file', str(ART / 'pr-body-initial.md')])
number = int(url.rsplit('/', 1)[-1])
save('pr-created.json', dict(url=url, number=number, initial_head=I['head']))
save('pr-initial.json', gh([f'repos/{REPO}/pulls/{number}']))
print(url)
