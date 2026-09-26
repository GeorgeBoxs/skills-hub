# skills-hub

Claude Code plugin marketplace consumed by all of the owner's project repos. Merging to `main` releases to every consumer via marketplace auto-update — treat every change as a release.

Rules:

- Every skill dir that is a mapping `to` in `sources.lock` is **vendored** from an upstream — today that is all of `plugins/*/skills/*` except `george-core`. Never hand-edit them: the sync workflow overwrites these directories wholesale. To customize a vendored skill, first remove its mapping from `sources.lock`, then edit.
- Own skills live in `plugins/george-core/skills/<name>/` (SKILL.md + optional references/ scripts/). New domain = new `plugins/<name>/` with `.claude-plugin/plugin.json` + an entry in `.claude-plugin/marketplace.json`.
- Plugin `version` fields are intentionally omitted everywhere so consumers track updates by git SHA. Do not add versions — adding one freezes consumer updates until it is bumped again.
- `scripts/sync_upstream.py` (stdlib-only, run from anywhere) refreshes vendored copies and bumps `sha` in `sources.lock`; it writes `SYNC_NOTES.md` with warnings and with skills added upstream since the previous sync that have no mapping yet (candidates — the owner decides which to vendor). The weekly workflow runs it and opens a PR with those notes as the body — review skill diffs before merging.
- Keep every skill self-contained: no cross-skill relative imports, no repo-specific assumptions (repo-specific skills belong in the consuming project's `.claude/skills/`).
