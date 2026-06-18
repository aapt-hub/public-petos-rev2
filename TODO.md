# TODO.md — Create public-petos-rev2 (16 pillars only)

## Plan from validated sources
Source docs: `FullPETOSArchitecture.txt`, `TODO_Layer_VALIDATION.md`

## Steps
- [x] Create MkDocs baseline config (`mkdocs.yml`) with strict-mode enabled at build time.

- [ ] Refactor `docs/pillar-*` structure to `stacks/<stack-name>`.
- [x] Add stack index pages (`index.md`) and capabilities pages (`capabilities/index.md`).
- [x] Configure `mkdocs.yml` navigation for all 16 stacks.
- [x] Consolidate validation scripts into `validate.py` at the repo root.
- [x] Update CI (`validate-and-build.yml`) to use new script paths.
- [x] Update `CONTRIBUTING.md` with new validation commands.
- [ ] Align repository with target blueprint structure.
  - [ ] Rename `LICENSE.md` to `LICENSE`.
  - [x] Update `CODEOWNERS`.
  - [x] Create `README.md` and `PULL_REQUEST_TEMPLATE.md`.
- [ ] Ensure `mkdocs build --strict` succeeds.
- [ ] Ensure `python validate.py` runs and produces/updates expected outputs.
- [ ] Update this TODO.md checkboxes as each step completes.
