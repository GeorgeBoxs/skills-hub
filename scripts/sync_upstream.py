#!/usr/bin/env python3
"""Refresh vendored upstream skills according to sources.lock.

For every source: shallow-clone its branch, copy each mapped skill directory
over the local copy (full replace), and record the new commit SHA in
sources.lock. A mapping whose upstream directory disappeared is kept locally
and reported as a warning. Results are summarized in SYNC_NOTES.md so the
sync PR diff carries its own review notes. Stdlib only; requires git.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / "sources.lock"


def run(*args: str, cwd: str | None = None) -> str:
    res = subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)
    return res.stdout.strip()


def main() -> int:
    lock = json.loads(LOCK_PATH.read_text())
    notes: list[str] = []
    warnings: list[str] = []

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
    (ROOT / "SYNC_NOTES.md").write_text("\n".join(lines) + "\n")

    print("\n".join(notes + warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
