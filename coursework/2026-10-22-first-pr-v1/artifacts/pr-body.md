## Goal
Complete the first pull request exercise by publishing the user guide change from `docs/preview`.

## Changes
Replace the old direct `git push origin main` example with `git push -u origin docs/preview` in `user-guide.md`. Keep the document's Chinese and Russian content.

## Validation
- Started `docs/preview` from the freshly synchronized `main` at `808a8d4cb69bd98b3756a39503d287d6546c7c34`.
- `git diff --check` passed.
- The diff changes only `user-guide.md`.
- The published branch matches initial commit `6908fedb650c19131913f551a7867eaf3105970d`.
- The author workspace is clean after pushing.

## Limitations
The user explicitly authorized a single-account automated classroom role demonstration. Both A and B actions use the authenticated `Zhi-Arman` account. Review comments and a later B-role confirmation will be recorded as automation; they do not establish a real student's execution or an independent GitHub APPROVE review. No business tests or VS Code visual preview were run.

## Review workflow
B-role automation will record one concrete review comment; A-role automation will make a follow-up commit; B-role automation will verify the correction before the owner merges. Keep `docs/preview` after merging.
