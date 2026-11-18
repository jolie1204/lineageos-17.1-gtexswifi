#!/usr/bin/env python3
"""Validate or apply the port's patches against the pinned project revisions."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


def git(project, *args, temporary_index=None):
    env = None
    if temporary_index is not None:
        env = {**os.environ, "GIT_INDEX_FILE": str(temporary_index)}
    return subprocess.check_output(["git", "-C", project, *args], env=env, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tree", type=Path, help="Root of the repo-synced Android source tree")
    parser.add_argument("--apply", action="store_true", help="Apply and stage the patches in a clean checkout")
    args = parser.parse_args()
    tree = args.tree.resolve()
    patch_dir = Path(__file__).resolve().parent / "patches"
    projects = json.loads((patch_dir / "manifest.json").read_text())["projects"]
    pending = []

    for entry in projects:
        project = (tree / entry["project"]).resolve()
        patch = patch_dir / entry["patch"]
        base = entry["base_commit"]
        if git(project, "rev-parse", "--show-toplevel") != str(project):
            parser.error(f"{project} is not the expected Git project root")
        if git(project, "rev-parse", "HEAD") != base:
            parser.error(f"{project} must be at {base}")
        if hashlib.sha256(patch.read_bytes()).hexdigest() != entry["sha256"]:
            parser.error(f"Checksum mismatch for {patch.name}")
        if args.apply:
            if git(project, "status", "--porcelain"):
                parser.error(f"{project} has existing changes")
            git(project, "apply", "--index", "--check", patch)
        else:
            with TemporaryDirectory() as temp:
                index = Path(temp) / "index"
                git(project, "read-tree", base, temporary_index=index)
                git(project, "apply", "--cached", "--check", patch, temporary_index=index)
        pending.append((project, patch))
        print(f"Checked {entry['project']}")

    if args.apply:
        for project, patch in pending:
            git(project, "apply", "--index", patch)
    action = "Applied" if args.apply else "Validated"
    print(f"{action} {len(pending)} patches.")


if __name__ == "__main__":
    main()
