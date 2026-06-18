"""Layer 2 validation for public-petos-rev2.

Validates that each of the core stacks has a capabilities landing page.

This repo intentionally only implements:
- Layer 1 = Stacks
- Layer 2 = Capabilities

Layers 3+ are placeholders.
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

    missing: list[str] = []

    for stack in EXPECTED_STACKS:
        cap_index = STACKS_DIR / stack / "capabilities" / "index.md"
        if not cap_index.exists():
            missing.append(f"{stack}/capabilities/index.md")

    # Optional: do not enforce capability detail pages yet to keep iteration fast.
    if missing:
        print("Missing Layer 2 capabilities landing pages:")
        for m in missing:
            print(f"- {m}")
        fail("Layer 2 validation failed")

    report_path = STACKS_DIR / "AUDIT_REPORT_LAYER_2_VALIDATION.md"
    report = """# Audit Report — Layer 2 Validation

This file is generated/updated by repository validation tooling.

## Status
- Capabilities landing pages: PASS

## Checked
- `stacks/<stack-name>/capabilities/index.md` presence for all core stacks
"""
    report_path.write_text(report, encoding="utf-8")

    print("Layer 2 validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
