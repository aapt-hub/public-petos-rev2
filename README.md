# PETOS vNext - Enterprise Knowledge Base

This repository is the single source of truth for engineering knowledge, architecture patterns, and operational best practices. It is built using a "docs-as-code" philosophy and rendered as a static site using [MkDocs](https://www.mkdocs.org/).

The core knowledge base is organized into technology `stacks/`.
All contributions are validated against a series of automated checks to ensure quality and consistency.

## Repository Structure

```text
├── .github/              # GitHub automation (CI, issue templates)
├── stacks/               # The core knowledge base content (for MkDocs)
├── templates/            # HTML templates for the validation dashboard
├── .gitignore
├── CONTRIBUTING.md       # How to contribute
├── LICENSE
├── README.md             # This file
├── dashboard.py          # Web-based validation dashboard
├── kb-article-template.md # Boilerplate for new articles
└── validate.py           # Command-line validation script
```

## Local Development

There are three main ways to interact with this repository locally.

### 1. Preview the Knowledge Base Site

To run the local development server and see how your changes look:

```bash
# Install dependencies (if you haven't already)
pip install -r requirements.txt

# Serve the site
python -m mkdocs serve
```
The site will be available at `http://127.0.0.1:8000` and will automatically reload when you save a file.

### 2. Run Validations (Command Line)

To ensure the structure and content meet our standards, run the validation script from the command line:

```bash
# Run all validation checks
python validate.py

# Or run a specific check (e.g., links)
python validate.py links
```

### 3. Run Validations (GUI Dashboard)

For a more user-friendly interface, you can use the web-based validation dashboard.

```bash
# Install Flask (if you haven't already)
pip install Flask

# Run the dashboard server
python dashboard.py
```
The dashboard will be available at `http://127.0.0.1:5001`.