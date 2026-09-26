# skills-hub

Personal hub of Claude skills: **the single marketplace that all my projects use**. It holds my own skills plus curated copies from upstream repositories. A merge to `main` is a release for every project (the marketplace auto-updates).

## Layout

```
.claude-plugin/marketplace.json   # marketplace manifest (10 plugins, 102 skills)
plugins/
  george-core/   # own skills (6)
  design/        # design and UX (7)
  landing-cro/   # landing pages and conversion (7)
  product/       # product (9)
  growth/        # growth and marketing (13)
  engineering/   # engineering (13)
  business/      # sales, revops, customer success (4)
  c-level/       # virtual C-suite and strategy (32)
  finance/       # finance and SaaS metrics (3)
  pm/            # project management (8)
sources.lock                      # where the vendored upstream skills come from, pinned to a SHA
scripts/sync_upstream.py          # refreshes the vendored copies per sources.lock
.github/workflows/sync-upstream.yml  # weekly sync → PR for review
```

## Using it in a project

In the project's `.claude/settings.json` (the project template already includes this):

```json
{
  "extraKnownMarketplaces": {
    "skills-hub": {
      "source": { "source": "github", "repo": "GeorgeBoxs/skills-hub" }
    }
  },
  "enabledPlugins": {
    "george-core@skills-hub": true,
    "design@skills-hub": true,
    "landing-cro@skills-hub": true,
    "product@skills-hub": true,
    "growth@skills-hub": true,
    "engineering@skills-hub": true
  }
}
```

Then, once per project: `/plugin install george-core@skills-hub` (and the other bundles). Skills are available as `george-core:ship-gate`, `engineering:database-designer`, and so on. The repo is private — consuming it works through your local git/gh access.

The business plugins (`business`, `c-level`, `finance`, `pm`) are intentionally left out of the
template's default `enabledPlugins` — install them as needed:
`/plugin install c-level@skills-hub`.

## How updates flow

- **Upstream → hub**: the `sync-upstream` workflow (Mondays 06:00 UTC, or manually via *Run workflow*) clones the upstreams from `sources.lock`, replaces the vendored copies, bumps the SHA and opens a PR. Reviewing the diff is the only manual step. `SYNC_NOTES.md` (also used as the PR description) shows warnings (e.g. a skill removed upstream) and new upstream skills with their descriptions.
- **New upstream skills** are not picked up automatically: the sync only refreshes what is mapped in `sources.lock`. To take a candidate from `SYNC_NOTES.md`, add its mapping to `sources.lock` and re-run `scripts/sync_upstream.py`.
- **Hub → projects**: nothing to do. Plugin versions are intentionally omitted — Claude Code tracks plugins by git SHA, so every merge to `main` reaches consumers automatically; `/plugin update` forces it.

## Rules

- **Don't edit** vendored skills — currently every plugin except `george-core` (the exact list is the `to` fields in `sources.lock`); the sync overwrites them. Need a change → either remove the mapping from `sources.lock` (the skill becomes your own) or contribute upstream.
- Own skills go in `plugins/george-core/skills/<name>/SKILL.md` (or a new plugin + an entry in `marketplace.json`).
- A new upstream source = a new entry in `sources.lock` (repo, branch, sha, mappings).
- Repo-specific skills (such as `repo-conventions`) do **not** belong here — they live in their own project's `.claude/skills/`.

## Licenses

The vendored skills are MIT-licensed, from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills); see `THIRD_PARTY_NOTICES.md` and the exact pin in `sources.lock`.
