Controlled conflict reproduced by automation in the authorized single-account classroom exercise.

A PR #2 merged first at `ab59f232f153fc8bd185e8783e3fd51f11302394`. Both branches start from `569a94ac86983d1180866f65126eee6d5efad6c0` and each changes only the single line in `docs/build-check.md`.

In the isolated B workspace, `git merge --no-ff --no-edit docs/conflict-b` from the updated `main` returned exit code 1 and a content conflict. `git status --porcelain=v1` reports `UU docs/build-check.md`. The index contains stages 1 (baseline), 2 (A/main), and 3 (B); MERGE_HEAD is `422324570163f036bb9b536b0f09f75eb6a846c5`. GitHub also reports this PR as conflicting.

This task ends at the conflict. B PR stays open, the B workspace stays in the unresolved merge state, and no resolution or merge abort was performed. Keep all branches. Sphinx build execution and business tests are NOT_RUN. This is not proof of the students' personal execution.