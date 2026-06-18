"""
Validates all relative markdown links in the `stacks/` directory.

This script is designed to be run from the repository root. It will:
1. Find all `.md` files within the `stacks/` directory.
2. Parse each file to find markdown-style links `text`.
3. Ignore absolute URLs (http://, https://) and mailto links.
4. For each relative link, resolve its path relative to the containing file.
5. Check if the resolved path points to an existing file.
6. If the link has an anchor (#heading), check if the heading exists in the target file.
6. Report any broken links and exit with a non-zero status code if any are found.
"""

from __future__ import annotations

import re
from pathlib import Path
import sys
from urllib.parse import unquote

# Cache for file slugs to avoid re-parsing the same file multiple times.
_slug_cache: dict[Path, set[str]] = {}


def slugify(text: str) -> str:
    """
    Converts a heading string to a URL-friendly slug.
    This mimics common markdown slug generation: lowercasing, removing most
    special characters, and replacing spaces with hyphens.
    """
    text = text.strip().lower()
    # Remove non-alphanumeric characters except spaces and hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    # Replace spaces and consecutive hyphens with a single hyphen
    text = re.sub(r"[\s-]+", "-", text)
    return text


def get_slugs_from_file(file_path: Path) -> set[str]:
    """Parses a markdown file and returns a set of slugs for its headings."""
    if file_path in _slug_cache:
        return _slug_cache[file_path]

    if not file_path.is_file():
        _slug_cache[file_path] = set()
        return set()

    content = file_path.read_text(encoding="utf-8")
    # Regex to find all markdown headings (lines starting with #, ##, etc.)
    heading_regex = re.compile(r"^(?:#{1,6})\s+(.*)", re.MULTILINE)
    headings = heading_regex.findall(content)

    slugs = {slugify(h) for h in headings}
    _slug_cache[file_path] = slugs
    return slugs


def main() -> int:
    """Main function to run the link validation."""
    repo_root = Path(__file__).resolve().parents[2]
    stacks_dir = repo_root / "stacks"

    # Regex to find markdown links that are not absolute URLs.
    # It captures the link destination, e.g., `path/to/file.md#anchor`.
    link_regex = re.compile(r"\[[^\]]+\]\(((?!https?://|mailto:)[^)\s]+)\)")

    if not stacks_dir.is_dir():
        print(f"ERROR: Stacks directory not found at {stacks_dir}")
        return 1

    all_markdown_files = list(stacks_dir.rglob("*.md"))
    broken_links: list[dict[str, str | Path]] = []

    for md_file in all_markdown_files:
        content = md_file.read_text(encoding="utf-8")
        found_links = link_regex.findall(content)

        for link in found_links:
            # Decode URL-encoded characters (e.g., %20 -> space)
            decoded_link = unquote(link)

            # Separate the file path from any anchor tag (#)
            if "#" in decoded_link:
                path_part, anchor_part = decoded_link.split("#", 1)
            else:
                path_part, anchor_part = decoded_link, None

            # Determine the target file for the link
            if not path_part:
                # This is an anchor-only link to the same file, e.g., `text`
                target_file = md_file
            else:
                # This is a link to a file, which may or may not have an anchor
                target_file = (md_file.parent / Path(path_part)).resolve()

            # 1. Validate that the target file exists
            if not target_file.is_file():
                broken_links.append(
                    {
                        "source_file": md_file.relative_to(repo_root),
                        "link": link,
                        "reason": f"File not found at resolved path: {target_file}",
                    }
                )
                continue  # No point checking anchor if file is missing

            # 2. If an anchor is present, validate it
            if anchor_part:
                target_slugs = get_slugs_from_file(target_file)
                if anchor_part not in target_slugs:
                    broken_links.append(
                        {
                            "source_file": md_file.relative_to(repo_root),
                            "link": link,
                            "reason": f"Anchor '#{anchor_part}' not found in {target_file.relative_to(repo_root)}",
                        }
                    )

    if broken_links:
        print("ERROR: Found broken relative links!\n")
        for broken in broken_links:
            print(f"- In File: {broken['source_file']}")
            print(f"  Broken Link: '{broken['link']}'")
            print(f"  Reason: {broken['reason']}")
            print("-" * 20)
        return 1

    print("Link validation: PASS. No broken relative links found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())