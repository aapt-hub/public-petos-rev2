# TODO.md — Create public-petos-rev2 (16 pillars only)

## Plan from validated sources
Source docs: `FullPETOSArchitecture.txt`, `TODO_Layer_VALIDATION.md`

## Steps
- [x] Create MkDocs baseline config (`mkdocs.yml`) with strict-mode enabled at build time.

- [x] Refactor `docs/pillar-*` structure to `stacks/<stack-name>`. (All 16 stacks created)
- [x] Add stack index pages (`index.md`) and capabilities pages (`capabilities/index.md`). (All 16 stacks created with front-matter)
- [x] Configure `mkdocs.yml` navigation for all 16 stacks.
- [x] Consolidate validation scripts into `validate.py` at the repo root.
- [x] Update CI (`validate-and-build.yml`) to use new script paths.
- [x] Update `CONTRIBUTING.md` with new validation commands.
- [x] Align repository with target blueprint structure.
  - [x] Rename `LICENSE.md` to `LICENSE`.
  - [x] Update `CODEOWNERS`.
  - [x] Create `README.md` and `PULL_REQUEST_TEMPLATE.md`.
- [ ] Ensure `mkdocs build --strict` succeeds.
- [x] Ensure `python validate.py` runs and produces/updates expected outputs.
- [ ] Update this TODO.md checkboxes as each step completes.
