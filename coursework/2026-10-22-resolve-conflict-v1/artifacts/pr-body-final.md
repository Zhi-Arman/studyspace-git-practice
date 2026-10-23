## Goal
Resolve the controlled conflict from the classroom exercise, actually build the documentation, and complete the B pull request.

## Changes
- Resolve `docs/build-check.md` to `.venv/bin/python -m sphinx -W -n -b html docs site`, retaining A's `-W` and B's `-n`.
- Remove all conflict markers and complete local merge commit `49de18441048777347d9c008e5ba4fe3149be977` with parents `ab59f232f153fc8bd185e8783e3fd51f11302394` and `422324570163f036bb9b536b0f09f75eb6a846c5`.
- Add the minimum working Sphinx setup: `docs/conf.py`, `docs/index.md`, the existing course's hashed `requirements-docs.txt`, and ignores for `.venv`, `site`, and Python caches.
- The index includes the repository's current user/admin guides and the resolved command. Exactly five files differ from main.

## Validation
- Ran the exact resolved command in the repository root with isolated Python 3.13.12, Sphinx 8.2.3, and MyST 4.0.1.
- Build exit code 0, zero warnings with `-W -n`; HTML index generated and verified to contain the resolved command and current guides.
- Hashed dependency installation and `uv pip check` passed.
- `git diff --check` passed before staging; no unmerged index entries or MERGE_HEAD remain after the local merge.
- The local merge has both original parents. The source branch was advanced by a normal fast-forward push, preserving history.

## Limitations
This remains the user's authorized single-account automated role demonstration with `Zhi-Arman`; there is no independent student APPROVE review. The build validates this documentation only; application business tests and teacher acceptance are not claimed. All exercise branches must remain after merging.
