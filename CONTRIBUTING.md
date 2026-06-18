# Contributing

This repository hosts **PETOS vNext** knowledge using **MkDocs**.

## Changes
- Keep documentation changes small and focused.
- Run validations before opening a pull request.

## Creating a New Article

1.  Copy the boilerplate from `templates/kb-article-template.md`.
2.  Create a new `.md` file in the relevant `stacks/<stack-name>/` directory (e.g., `stacks/operations-observability/new-monitoring-guide.md`).
3.  Paste the template content and fill out the sections, replacing all bracketed `[...]` placeholders.
4.  Ensure the YAML front-matter (`title`, `description`, `tags`) is updated to be specific to your article.

## Validation
From repo root:
- `python validate.py`
- `mkdocs build --strict`

## Pull Requests
- Follow the PR template.
- Include an explanation of what changed and why.
