# TODO — Layer Validation (public-petos-rev2)

## Goal
Create a new repository layout following **FullPetosArchitecture** and ensure MkDocs strict-mode + Layer 0/1 validation pass.

## Steps
- [ ] Copy existing repo into `public-petos-rev2/` (excluding build artifacts).
- [ ] Implement new directory architecture mapping per FullPetosArchitecture.
- [ ] Update `mkdocs.yml` nav to match new paths.
- [ ] Fix/verify all MkDocs strict-mode validation issues (`python -m mkdocs build --strict`).
- [ ] Run `python validate.py` and review any generated reports.
- [ ] Ensure case-sensitive filenames are consistent; do not introduce casing mismatches.
- [ ] Finalize README + root docs references.
