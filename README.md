# PETOS vNext - Enterprise Knowledge Base

This repository is the single source of truth for engineering knowledge, architecture patterns, and operational best practices. It is built using a "docs-as-code" philosophy and rendered as a static site using [MkDocs](https://www.mkdocs.org/).

The core knowledge base is organized into technology `stacks/`.

## Repository Structure

```
├── .github/         # GitHub automation (CI, issue templates)
├── architecture/    # System diagrams and blueprints
├── automation/      # Validation scripts and tooling
├── stacks/          # The core knowledge base content (for MkDocs)
├── templates/       # Boilerplate for articles and configs
├── .gitignore
├── CONTRIBUTING.md  # How to contribute
├── LICENSE
└── README.md        # This file
```

## Local Development

1.  **Run Validations**: Ensure the structure and content meet standards.
    ```bash
    # Run all validation checks
    python validate.py

    # Or run a specific check
    python validate.py links
    ```

2.  **Build & Serve Site**:
    ```bash
    pip install mkdocs mkdocs-material
    mkdocs serve
    ```
    The site will be available at `http://127.0.0.1:8000`.