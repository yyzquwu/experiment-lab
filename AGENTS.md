# Repo Notes

## Narrative style
- Keep README, reports, and notes in a personal, human voice.
- Avoid recruiter language, tutorial voice, and generic promotional framing.
- Let the context differ by case: explain what changed, what felt convincing, and what still felt fragile in that specific area.
- Do not reuse the same narrative paragraph across folders or artifacts.

## Data provenance
- Be explicit about whether a case uses real public data or synthetic stress-test data.
- Keep `data/raw/` ignored by git.
- If a public dataset is added, prefer scripted download + preprocessing over committing the raw file.

## GitHub hygiene
- Keep commits scoped and descriptive.
- Avoid committing secrets, tokens, or local env files.
- Update `README.md`, `case_studies/README.md`, and generated reports when a case-study surface changes.
- Prefer reproducible commands (`make test`, `make demo`) over hand-waved instructions.
