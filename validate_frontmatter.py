"""
Validates the YAML front-matter of all markdown files in the `stacks/` directory.

This script ensures that:
1. Each markdown file contains a YAML front-matter block.
2. The front-matter is valid YAML.
3. The front-matter contains the required keys (`title`, `description`).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Please run 'pip install PyYAML' or add it to your requirements.", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    """Main function to validate front-matter."""
    repo_root = Path(__file__).resolve().parents[2]
    stacks_dir = repo_root / "stacks"
    required_keys = {"title", "description"}
    errors = []

    # Regex to extract the YAML front-matter block.
    front_matter_pattern = re.compile(r"^---\s*\n(.*?)\n^---\s*\n", re.DOTALL | re.MULTILINE)

    all_md_files = [
        p for p in stacks_dir.rglob("*.md")
        if not p.name.startswith("AUDIT_REPORT")
    ]

    for md_file in all_md_files:
        relative_path = md_file.relative_to(repo_root)
        try:
            content = md_file.read_text(encoding="utf-8")
            match = front_matter_pattern.match(content)

            if not match:
                errors.append(f"- {relative_path}: Missing YAML front-matter block.")
                continue

            front_matter_str = match.group(1)
            data = yaml.safe_load(front_matter_str)

            if not isinstance(data, dict):
                errors.append(f"- {relative_path}: Front-matter is not a valid key-value structure.")
                continue

            missing_keys = required_keys - set(data.keys())
            if missing_keys:
                errors.append(f"- {relative_path}: Missing required keys: {', '.join(sorted(list(missing_keys)))}")

        except yaml.YAMLError as e:
            errors.append(f"- {relative_path}: Invalid YAML syntax: {e}")
        except Exception as e:
            errors.append(f"- {relative_path}: Could not read or process file: {e}")

    if not errors:
        print("Front-matter validation: PASS. All files have valid front-matter.")
        return 0

    print("\nERROR: Found issues with front-matter in the following files:")
    for error in errors:
        print(error)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())