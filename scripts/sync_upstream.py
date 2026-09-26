#!/usr/bin/env python3
"""Refresh vendored upstream skills according to sources.lock.

For every source: shallow-clone its branch, copy each mapped skill directory
over the local copy (full replace), and record the new commit SHA in
sources.lock. A mapping whose upstream directory disappeared is kept locally
and reported as a warning. Skills added upstream since the previous sync that
have no mapping yet are listed with their descriptions as candidates to
vendor. Results are summarized in SYNC_NOTES.md so the sync PR diff carries
its own review notes. Stdlib only; requires git.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / "sources.lock"


def run(*args: str, cwd: str | None = None) -> str:
    res = subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)
    return res.stdout.strip()


def added_skill_dirs(clone: str, old_sha: str) -> list[str]:
    """Directories whose SKILL.md appeared between old_sha and HEAD.

    Hidden trees are skipped: upstreams mirror their skills there for other
    tools (e.g. `.gemini/`).
    """
    run("git", "-C", clone, "fetch", "--depth", "1", "origin", old_sha)
    added = run(
        "git", "-C", clone, "diff", "-z", "--name-only", "--no-renames",
        "--diff-filter=A", old_sha, "HEAD",
    )
    dirs = []
    for path in map(PurePosixPath, added.split("\0")):
        parts = path.parent.parts
        if path.name == "SKILL.md" and parts and not any(p.startswith(".") for p in parts):
            dirs.append(path.parent.as_posix())
    return sorted(dirs)


def describe(skill_md: Path) -> str:
    """The frontmatter `description` of a SKILL.md, shortened for the notes."""
    try:
        lines = skill_md.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return "(unreadable SKILL.md)"
    if not lines or lines[0].strip() != "---":
        return "(no frontmatter)"
    parts: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if parts:  # inside the description: indented lines continue it
            if not line[:1].isspace():
                break
            parts.append(line.strip())
        elif line.startswith("description:"):
            value = line.removeprefix("description:").strip()
            parts.append("" if value[:1] in (">", "|") else value)  # block scalar
    text = " ".join(filter(None, parts))
    if len(text) > 1 and text[0] in "\"'" and text[-1] == text[0]:
        text = text[1:-1]
    return textwrap.shorten(text, 200, placeholder="…") or "(no description)"


def main() -> int:
    lock = json.loads(LOCK_PATH.read_text())
    notes: list[str] = []
    warnings: list[str] = []
    candidates: dict[str, list[str]] = {}

    for source in lock["sources"]:
        repo = source["repo"]
        branch = source.get("branch", "main")
        with tempfile.TemporaryDirectory() as tmp:
            run("git", "clone", "--depth", "1", "--branch", branch, repo, tmp)
            new_sha = run("git", "-C", tmp, "rev-parse", "HEAD")
            old_sha = source.get("sha", "")

            for mapping in source["mappings"]:
                src = Path(tmp) / mapping["from"]
                dest = ROOT / mapping["to"]
                if not (src / "SKILL.md").is_file():
                    warnings.append(
                        f"`{mapping['from']}` is gone from {repo} @ {new_sha[:7]} — "
                        f"local copy `{mapping['to']}` kept as-is; fix the mapping or drop it"
                    )
                    continue
                if dest.exists():
                    shutil.rmtree(dest)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src, dest)

            if old_sha and old_sha != new_sha:
                try:
                    added = added_skill_dirs(tmp, old_sha)
                except subprocess.CalledProcessError as err:
                    print(err.stderr, file=sys.stderr)
                    warnings.append(
                        f"could not fetch the previous {repo} @ {old_sha[:7]} — "
                        f"new-skill check skipped"
                    )
                    added = []
                mapped = [m["from"] for m in source["mappings"]]
                fresh = [
                    d for d in added
                    if not any(d == m or d.startswith(m + "/") for m in mapped)
                ]
                if fresh:
                    candidates[repo] = [
                        f"`{d}` — {describe(Path(tmp) / d / 'SKILL.md')}" for d in fresh
                    ]

            source["sha"] = new_sha
            notes.append(
                f"{repo}: `{old_sha[:7] or 'none'}` → `{new_sha[:7]}` "
                f"({len(source['mappings'])} mappings)"
            )

    LOCK_PATH.write_text(json.dumps(lock, indent=2) + "\n")

    lines = ["# Last upstream sync", ""]
    lines += [f"- {n}" for n in notes]
    if warnings:
        lines += ["", "## Warnings", ""] + [f"- ⚠️ {w}" for w in warnings]
    if candidates:
        lines += [
            "",
            "## New upstream skills (not vendored)",
            "",
            "Added upstream since the previous sync. To vendor one, add its mapping to",
            "`sources.lock` and re-run `scripts/sync_upstream.py`.",
            "",
        ]
        for repo, entries in candidates.items():
            lines += [f"- {repo}"] + [f"  - {e}" for e in entries]
    text = "\n".join(lines) + "\n"
    (ROOT / "SYNC_NOTES.md").write_text(text)

    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
