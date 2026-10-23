## Goal
Complete the controlled merge-conflict exercise in the shared classroom repository.

## Changes
Add the shared baseline `docs/build-check.md` from commit `569a94ac86983d1180866f65126eee6d5efad6c0`, then change only its one command line on `docs/conflict-b`.
The role B commit is `422324570163f036bb9b536b0f09f75eb6a846c5`. A enables `-W`; B enables `-n` in the same line.

## Validation
- A and B branches have exactly the same parent `569a94ac86983d1180866f65126eee6d5efad6c0`.
- Each role changes only one line in `docs/build-check.md` relative to that parent.
- `git diff --check` passed and both published worktrees are clean.

## Workflow
Merge A first. Then attempt B into the updated main and preserve the expected conflict without resolving or aborting it. Keep all exercise branches.

## Limitations
This is the user's authorized single-account automated A/B role demonstration using `Zhi-Arman`, not personal execution or independent approval by students. Sphinx commands are exercise text only: the shared repository has no full Sphinx configuration, so build execution and business tests are NOT_RUN.
