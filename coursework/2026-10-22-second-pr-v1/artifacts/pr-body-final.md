## Change
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

## Review correction and confirmation
- Initial review head: `506f4276fe290680231415a9a2d50a4f15fd1358`.
- Automated reviewer checked marker absence and bilingual wording, then requested one explicit tracked-Markdown marker scan with exit-code interpretation.
- One correction commit: `e7bf2c55af0010e5259dbf55082486c5d0d95a78`. It changes only `docs/index.md` and adds the scan plus paired Chinese/Russian explanations: 1 = no matches, 0 = markers found, greater than 1 = execution error.
- Reran diff/index/marker checks and the exact real Sphinx build: exit 0, zero warnings.
- Confirmation is recorded as a separate automated reviewer-role COMMENT tied to the corrected head, not as an independent GitHub APPROVE.
