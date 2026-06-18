"""
Validates that the .github/CODEOWNERS file is in sync with the `stacks/` directories.

This script ensures that:
1. Every stack directory in `stacks/` has a corresponding ownership rule.
2. Every stack ownership rule in CODEOWNERS corresponds to an existing directory.
"""

from __future__ import annotations

import re
from pathlib import Path
import sys


def main() -> int:
    """Main function to run the CODEOWNERS validation."""
    repo_root = Path(__file__).resolve().parents[2]
    stacks_dir = repo_root / "stacks"
    codeowners_path = repo_root / ".github" / "CODEOWNERS"

    if not codeowners_path.is_file():
        codeowners_md_path = repo_root / ".github" / "CODEOWNERS.md"
        if codeowners_md_path.is_file():
            print("WARNING: Found '.github/CODEOWNERS.md'. This file should be renamed to '.github/CODEOWNERS' for GitHub to process it correctly.")
            codeowners_path = codeowners_md_path
        else:
            print(f"ERROR: CODEOWNERS file not found at {codeowners_path}")
            return 1

    if not stacks_dir.is_dir():
        print(f"ERROR: Stacks directory not found at {stacks_dir}")
        return 1

    # 1. Get all immediate subdirectories from the `stacks/` directory.
    try:
        filesystem_stacks = {d.name for d in stacks_dir.iterdir() if d.is_dir()}
    except OSError as e:
        print(f"ERROR: Could not read directories from {stacks_dir}: {e}")
        return 1

    # 2. Parse CODEOWNERS to find all defined stack owners.
    codeowners_stacks = set()
    # Regex to match lines like: /stacks/stack-name/ @owner
    stack_owner_pattern = re.compile(r"^\s*/stacks/([a-zA-Z0-9_-]+)/?\s+@\S+")

    content = codeowners_path.read_text(encoding="utf-8")
    for line in content.splitlines():
        match = stack_owner_pattern.match(line)
        if match:
            codeowners_stacks.add(match.group(1))

    # 3. Compare the two sets to find discrepancies.
    missing_from_codeowners = filesystem_stacks - codeowners_stacks
    orphaned_in_codeowners = codeowners_stacks - filesystem_stacks

    if not missing_from_codeowners and not orphaned_in_codeowners:
        print("CODEOWNERS validation: PASS. All stacks are correctly mapped.")
        return 0

    if missing_from_codeowners:
        print("\nERROR: Found stack directories missing from .github/CODEOWNERS:")
        for stack in sorted(list(missing_from_codeowners)):
            print(f"- '{stack}' exists in 'stacks/' but has no owner. Suggestion: Add '/stacks/{stack}/ @your-org/team-name' to CODEOWNERS.")
    if orphaned_in_codeowners:
        print("\nERROR: Found orphaned stack entries in .github/CODEOWNERS:")
        for stack in sorted(list(orphaned_in_codeowners)):
            print(f"- An owner is assigned for '/stacks/{stack}/', but this directory does not exist.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())