"""
Finds orphaned markdown files in the `stacks/` directory.

An orphan is a markdown file that is not linked to from any other file
and is not a direct entry point in the `mkdocs.yml` navigation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Please run 'pip install PyYAML' or add it to your requirements.", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    """Main function to find orphaned markdown files."""
    repo_root = Path(__file__).resolve().parents[2]
    stacks_dir = repo_root / "stacks"
    mkdocs_yml_path = repo_root / "mkdocs.yml"

    # 1. Get all markdown files, excluding generated audit reports.
    all_md_files = {
        p.resolve() for p in stacks_dir.rglob("*.md")
        if not p.name.startswith("AUDIT_REPORT")
    }

    # 2. Find all files that are linked to from other markdown files.
    link_regex = re.compile(r"\[[^\]]+\]\(((?!https?://|mailto:)[^)\s]+)\)")
    linked_files = set()
    for md_file in all_md_files:
        content = md_file.read_text(encoding="utf-8")
        for link in link_regex.findall(content):
            path_part = unquote(link).split("#")[0]
            if path_part and path_part.endswith(".md"):
                target_path = (md_file.parent / Path(path_part)).resolve()
                linked_files.add(target_path)

    # 3. Find all files used as navigation entry points in mkdocs.yml.
    nav_files = set()
    with open(mkdocs_yml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    def extract_nav_paths(nav_item):
        if isinstance(nav_item, str) and nav_item.endswith(".md"):
            nav_files.add((stacks_dir / nav_item).resolve())
        elif isinstance(nav_item, dict):
            for value in nav_item.values():
                extract_nav_paths(value)
        elif isinstance(nav_item, list):
            for item in nav_item:
                extract_nav_paths(item)

    if "nav" in config:
        extract_nav_paths(config["nav"])

    # 4. An orphan is a file that is not linked to AND not in the nav.
    orphaned_files = all_md_files - linked_files - nav_files

    if not orphaned_files:
        print("Orphan validation: PASS. No orphaned articles found.")
        return 0

    print("\nERROR: Found orphaned markdown files!")
    for orphan in sorted(list(orphaned_files)):
        print(f"- {orphan.relative_to(repo_root)}")
    print("\nSuggestion: Link to these files from another article, add them to mkdocs.yml nav, or remove them.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())