# AGENTS.md

Account-wide conventions for `gjcourt` repositories: the README standard, its
templates, and the reusable check.

## Rules

- **Branch + PR** for every change; never commit to `main`.
- `scripts/readme_check.py` stays **stdlib-only** — the reusable workflow runs
  it with no install step.
- The check judges **structure only**. Don't add prose, length or style rules
  to it; those belong in review.
- **Every template must pass the check**, and CI enforces that. Change the
  check, its tests (`python3 -m unittest discover -s tests`) and the
  templates together.
- The reusable workflow is consumed at `@main` by other repos: a breaking
  change to the check breaks their next README PR. Loosen before tightening,
  and say so in the PR.
