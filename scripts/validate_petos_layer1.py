"""Layer 1 validation for public-petos-rev2.

This repo currently scaffolds the MkDocs site and stack docs. The validator is
intended to:
- Confirm that the core stack directories exist.
- Confirm that each stack has an index.md.
- Optionally enforce naming/casing rules.

It is written to be safe to run even before full content is populated.
"""

from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
STACKS_DIR = REPO_ROOT / "stacks"

EXPECTED_STACKS = [
    "infrastructure",
    "cloud-platforms",
    "digital-workplace",
    "cybersecurity",
    "development-automation",
    "data-platforms",
    "ai-engineering",
    "operations-observability",
    "service-management",
    "migration-engineering",
    "business-continuity",
    "architecture",
    "governance-compliance",
    "documentation-engineering",
    "career-development",
    "lessons-learned",
]


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}")
    sys.exit(code)


def main() -> int:
    if not STACKS_DIR.exists():
        fail(f"stacks directory not found at {STACKS_DIR}")

    missing_dirs: list[str] = []
    missing_indexes: list[str] = []

    for stack in EXPECTED_STACKS:
        stack_dir = STACKS_DIR / stack
        if not stack_dir.exists():
            missing_dirs.append(stack)
            continue

        idx = stack_dir / "index.md"
        if not idx.exists():
            missing_indexes.append(f"{stack}/index.md")

    if missing_dirs or missing_indexes:
        if missing_dirs:
            print("Missing stack dirs:")
            for d in missing_dirs:
                print(f"- {d}")
        if missing_indexes:
            print("Missing stack index.md:")
            for i in missing_indexes:
                print(f"- {i}")
        fail("Layer 1 validation failed")

    # Update audit report with a minimal summary.
    report_path = STACKS_DIR / "AUDIT_REPORT_LAYER_0_VALIDATION.md"
    report = """# Audit Report — Layer 0 Validation

This file is generated/updated by repository validation tooling.

## Status
- Layer 1 directory/index checks: PASS

## Checked
- Core stack directories presence
- `index.md` presence in each stack
"""
    report_path.write_text(report, encoding="utf-8")
    print("Layer 1 validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
