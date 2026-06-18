# Contributing

This repository hosts **PETOS vNext** knowledge using **MkDocs**.

## Getting Started

Before you begin, make sure you have all the required Python packages installed from the repository root.

```bash
pip install -r requirements.txt
```

## Contribution Workflow

### 1. Create a New Article

1.  Copy the content from `kb-article-template.md` (located in the repository root).
2.  Create a new `.md` file in the relevant `stacks/<stack-name>/` directory (e.g., `stacks/operations-observability/new-guide.md`).
3.  Paste the template content and fill it out, replacing all `[...]` placeholders.
4.  Ensure the YAML front-matter (`title`, `description`, `tags`) is specific to your article.

### 2. Preview Your Changes

Run the local development server to see how your changes look. The site will be available at `http://127.0.0.1:8000` and will automatically reload when you save a file.

```bash
python -m mkdocs serve
```

### 3. Run Validations

Before creating a pull request, run all local validation checks from the repository root to ensure quality and consistency.

```bash
# Run all custom repository validation checks
python validate.py

# Run the MkDocs strict build check
python -m mkdocs build --strict
```
