"""
Comprehensive, configurable validation script for the PETOS Knowledge Base.

This script combines all validation checks into a single entry point.
It can be configured to run all checks (default) or specific checks.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Please run 'pip install PyYAML'.", file=sys.stderr)
    sys.exit(1)

from typing import Any

# --- Constants and Helpers ---
REPO_ROOT = Path(__file__).resolve().parent
STACKS_DIR = REPO_ROOT / "stacks"
_SLUG_CACHE: dict[Path, set[str]] = {}

def slugify(text: str) -> str:
    """Converts a heading string to a URL-friendly slug."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text

def get_slugs_from_file(file_path: Path) -> set[str]:
    """Parses a markdown file and returns a set of slugs for its headings."""
    if file_path in _SLUG_CACHE:
        return _SLUG_CACHE[file_path]
    if not file_path.is_file():
        _SLUG_CACHE[file_path] = set()
        return set()
    content = file_path.read_text(encoding="utf-8")
    heading_regex = re.compile(r"^(?:#{1,6})\s+(.*)", re.MULTILINE)
    headings = heading_regex.findall(content)
    slugs = {slugify(h) for h in headings}
    _SLUG_CACHE[file_path] = slugs
    return slugs

# --- Validation Functions ---

def validate_structure() -> list[str]:
    """Validates Layers 1 & 2: stack directories, indexes, and capabilities pages."""
    EXPECTED_STACKS = [
        "infrastructure", "cloud-platforms", "digital-workplace", "cybersecurity",
        "development-automation", "data-platforms", "ai-engineering", "operations-observability",
        "service-management", "migration-engineering", "business-continuity", "architecture",
        "governance-compliance", "documentation-engineering", "career-development", "lessons-learned",
    ]
    errors: list[str] = []
    if not STACKS_DIR.is_dir():
        errors.append(f"FATAL: `stacks` directory not found at {STACKS_DIR}")
        return errors

    missing_dirs: list[str] = []
    missing_indexes: list[str] = []
    missing_caps: list[str] = []
    for stack in EXPECTED_STACKS:
        stack_dir = STACKS_DIR / stack
        if not stack_dir.is_dir():
            missing_dirs.append(stack)
            continue
        if not (stack_dir / "index.md").is_file():
            missing_indexes.append(f"{stack}/index.md")
        if not (stack_dir / "capabilities" / "index.md").is_file():
            missing_caps.append(f"{stack}/capabilities/index.md")

    if missing_dirs: errors.extend(["Missing stack directories:", *[f"- {d}" for d in missing_dirs]])
    if missing_indexes: errors.extend(["Missing stack index.md files:", *[f"- {i}" for i in missing_indexes]])
    if missing_caps: errors.extend(["Missing Layer 2 capabilities pages:", *[f"- {m}" for m in missing_caps]])

    return errors

def validate_codeowners() -> list[str]:
    """Validates that .github/CODEOWNERS is in sync with `stacks/` directories."""
    codeowners_path = REPO_ROOT / ".github" / "CODEOWNERS"
    errors: list[str] = []
    if not codeowners_path.is_file():
        errors.append(f"CODEOWNERS file not found at {codeowners_path}")
        if (REPO_ROOT / ".github" / "CODEOWNERS.md").is_file():
            errors.append("Hint: Found 'CODEOWNERS.md'. It should be named 'CODEOWNERS'.")
        return errors

    filesystem_stacks = {d.name for d in STACKS_DIR.iterdir() if d.is_dir()}
    codeowners_stacks: set[str] = set()
    stack_owner_pattern = re.compile(r"^\s*/stacks/([a-zA-Z0-9_-]+)/?\s+@\S+")
    content = codeowners_path.read_text(encoding="utf-8")
    for line in content.splitlines():
        if match := stack_owner_pattern.match(line):
            codeowners_stacks.add(match.group(1))

    if missing := filesystem_stacks - codeowners_stacks:
        errors.extend(["Found stack directories missing from .github/CODEOWNERS:", *[f"- '/stacks/{s}/' has no owner." for s in sorted(list(missing))]])
    if orphaned := codeowners_stacks - filesystem_stacks:
        errors.extend(["Found orphaned stack entries in .github/CODEOWNERS:", *[f"- An owner is assigned for '/stacks/{s}/', but this directory does not exist." for s in sorted(list(orphaned))]])

    return errors

def validate_links() -> list[str]:
    """Validates all relative markdown links and anchors in the `stacks/` directory."""
    link_regex = re.compile(r"\[[^\]]+\]\(((?!https?://|mailto:)[^)\s]+)\)")
    all_markdown_files = list(STACKS_DIR.rglob("*.md"))
    broken_links: list[str] = []
    for md_file in all_markdown_files:
        for link in link_regex.findall(md_file.read_text(encoding="utf-8")):
            path_part, anchor_part = (unquote(link).split("#", 1) + [None])[:2]
            target_file = md_file if not path_part else (md_file.parent / Path(path_part)).resolve()
            if not target_file.is_file():
                broken_links.append(f"In File: {md_file.relative_to(REPO_ROOT)}\n  Link: '{link}'\n  Reason: File not found.")
                continue
            if anchor_part and anchor_part not in get_slugs_from_file(target_file):
                broken_links.append(f"In File: {md_file.relative_to(REPO_ROOT)}\n  Link: '{link}'\n  Reason: Anchor '#{anchor_part}' not found in {target_file.relative_to(REPO_ROOT)}.")

    return broken_links

def validate_orphans() -> list[str]:
    """Finds orphaned markdown files that are not linked or in the site navigation."""
    all_md_files = {p.resolve() for p in STACKS_DIR.rglob("*.md") if not p.name.startswith("AUDIT_REPORT")}
    linked_files: set[Path] = set()
    nav_files: set[Path] = set()
    errors: list[str] = []
    link_regex = re.compile(r"\[[^\]]+\]\(((?!https?://|mailto:)[^)\s]+)\)")
    for md_file in all_md_files:
        for link in link_regex.findall(md_file.read_text(encoding="utf-8")):
            if (path_part := unquote(link).split("#")[0]) and path_part.endswith(".md"):
                linked_files.add((md_file.parent / Path(path_part)).resolve())

    with open(REPO_ROOT / "mkdocs.yml", "r", encoding="utf-8") as f: config = yaml.safe_load(f)
    def extract_nav(item: Any):
        if isinstance(item, str) and item.endswith(".md"): nav_files.add((STACKS_DIR / item).resolve())
        elif isinstance(item, dict): [extract_nav(v) for v in item.values()] # type: ignore
        elif isinstance(item, list): [extract_nav(i) for i in item] # type: ignore
    if "nav" in config: extract_nav(config["nav"])

    if orphaned_files := all_md_files - linked_files - nav_files:
        errors.append("Found orphaned markdown files:")
        errors.extend([f"- {orphan.relative_to(REPO_ROOT)}" for orphan in sorted(list(orphaned_files))])
        errors.append("\nSuggestion: Link to these files, add them to mkdocs.yml, or remove them.")
    return errors

def validate_frontmatter() -> list[str]:
    """Validates the YAML front-matter of all markdown files."""
    required_keys = {"title", "description", "tags"}
    errors: list[str] = []
    pattern = re.compile(r"^---\s*\n(.*?)\n^---\s*\n", re.DOTALL | re.MULTILINE)
    for md_file in [p for p in STACKS_DIR.rglob("*.md") if not p.name.startswith("AUDIT_REPORT")]:
        rel_path = md_file.relative_to(REPO_ROOT)
        try:
            match = pattern.match(md_file.read_text(encoding="utf-8"))
            if not match:
                errors.append(f"- {rel_path}: Missing YAML front-matter block.")
                continue
            data = yaml.safe_load(match.group(1))
            if not isinstance(data, dict):
                errors.append(f"- {rel_path}: Front-matter is not a valid key-value structure.")
                continue

            if missing_keys := required_keys - set(data.keys()):
                errors.append(f"- {rel_path}: Missing required keys: {', '.join(sorted(list(missing_keys)))}")
                continue  # Can't validate tags if the key is missing

            # Validate tags format and content
            tags = data.get("tags")
            if not isinstance(tags, list):
                errors.append(f"- {rel_path}: The 'tags' key must contain a list (e.g., `tags: [tag1, tag2]`).")
                continue

            invalid_tags = []
            for tag in tags:
                if not isinstance(tag, str) or tag != tag.lower() or " " in tag:
                    invalid_tags.append(f"'{tag}'")
            if invalid_tags:
                errors.append(f"- {rel_path}: Found invalid tags ({', '.join(invalid_tags)}). Tags must be lowercase strings with no spaces.")
        except yaml.YAMLError as e: errors.append(f"- {rel_path}: Invalid YAML syntax: {e}")
        except Exception as e: errors.append(f"- {rel_path}: Could not process file: {e}")

    return errors

def write_report(report_path: Path, summary: dict[str, str], details: dict[str, list[str]]):
    """Writes a validation summary to a markdown file."""
    from datetime import datetime, timezone

    report_content = [
        "# Validation Report",
        f"**Generated on:** {datetime.now(timezone.utc).isoformat()}",
        "\n## Summary\n",
        "| Check           | Status |",
        "| --------------- | ------ |",
    ]
    for name, status in summary.items():
        report_content.append(f"| {name:<15} | {status} |")

    if details:
        report_content.append("\n## Failure Details\n")
        for name, errors in details.items():
            report_content.append(f"### {name.title()} Validation Failed\n")
            report_content.append("```text")
            report_content.extend(errors)
            report_content.append("```\n")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_content), encoding="utf-8")
    print(f"\nReport written to {report_path}")

# --- Main CLI ---

def main() -> int:
    """Main entry point for the validation script."""
    all_checks = {
        "structure": validate_structure, "codeowners": validate_codeowners,
        "links": validate_links, "orphans": validate_orphans, "frontmatter": validate_frontmatter,
    }
    parser = argparse.ArgumentParser(description="PETOS Knowledge Base Validator.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("checks", nargs="*", choices=list(all_checks.keys()) + ["all"], help=f"Which check(s) to run. Options: {', '.join(all_checks.keys())}. If none are specified, 'all' is run.")
    parser.add_argument("--report-file", type=Path, help="Path to write a markdown report file.")
    args = parser.parse_args()

    # If no checks are provided on the command line, default to running all.
    checks_provided = args.checks if args.checks else ["all"]
    checks_to_run = list(all_checks.keys()) if "all" in checks_provided else checks_provided
    print(f"Running validations: {', '.join(checks_to_run)}\n" + "-" * 40)

    summary: dict[str, str] = {}
    details: dict[str, list[str]] = {}
    for name in checks_to_run:
        print(f"Running {name} validation...")
        try:
            if errors := all_checks[name]():
                summary[name] = "FAILED"
                details[name] = errors
            else:
                summary[name] = "PASSED"
        except Exception as e:
            summary[name] = "CRASHED"
            details[name] = [f"The check crashed with an unhandled exception: {e}"]

    print("\n--- Validation Summary ---")
    total_failures = 0
    for name, status in summary.items():
        print(f"{name:<15}: {status}")
        if status != "PASSED": total_failures += 1
    print("-" * 28)

    if details:
        print("\n--- Failure Details ---")
        for name, errors in details.items():
            print(f"\n[{name.upper()}]")
            for error in errors:
                print(error)

    if args.report_file:
        write_report(args.report_file, summary, details)

    if total_failures > 0:
        print(f"\n{total_failures} validation task(s) failed.")
        return 1
    print("\nAll selected validations passed successfully!")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())