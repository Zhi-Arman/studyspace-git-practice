## Goal
Complete the first pull request exercise with a small user-guide clarification on `docs/preview`.

## Changes
- Replace the old direct `main` push example with `git push -u origin docs/preview`.
- Address the review finding by checking `git branch --show-current` before staging and committing. Both Chinese and Russian instructions require `docs/preview` and stopping on a mismatch.
- The final diff changes only `user-guide.md`.

## Validation
- Branch started from freshly synchronized `main` at `808a8d4cb69bd98b3756a39503d287d6546c7c34`.
- Initial change: `6908fedb650c19131913f551a7867eaf3105970d`; review correction: `438984ac3a265512fbd0dff6471ce03797a152db`.
- `git diff --check` passed for the correction and full PR diff.
- The separate B workspace fetched the corrected commit, reported `docs/preview`, matched the remote head, and had a clean worktree.
- The concrete inline review thread was addressed and resolved; the B-role automated COMMENT confirmation is anchored to `438984ac3a265512fbd0dff6471ce03797a152db`.

## Limitations
This is a single-account automated classroom role demonstration explicitly authorized by the user. A and B actions use `Zhi-Arman`; they are not evidence of the named students' personal execution. Review and confirmation use COMMENT, not an independent APPROVE review. VS Code visual preview and business tests were not run. The source branch must remain after merging.
