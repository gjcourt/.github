<!-- readme-type: content -->
# .github

Account-wide conventions: the README standard, templates, and the reusable README check

The conventions every public `gjcourt` code repository follows, kept in one
place so they don't drift repo by repo. Start with the
[README standard](README-STANDARD.md).

**Status:** the README standard is new (2026-09); repos are adopting it one PR at a time.

## Layout

```text
README-STANDARD.md                     the standard: principles, skeleton, types, style
templates/readme/                      one starting README per type (tool, service, exporter, infra, content)
scripts/readme_check.py                structural check (stdlib Python; structure only, never prose)
tests/                                 unit tests for the check
.github/workflows/readme-check.yml     reusable workflow other repos call
.github/workflows/ci.yml               runs the tests, checks the templates and this README
```

## Conventions

Adopting the standard in a repo is one PR: pick the type, move the README onto
the skeleton, run every command in it, set the GitHub About description to the
tagline, and add the workflow from
[README-STANDARD.md § The check](README-STANDARD.md#the-check). Run the check
locally with:

```bash
python3 scripts/readme_check.py path/to/README.md --description "$(gh api repos/gjcourt/REPO --jq '.description // ""')"
```

Changes to the standard itself go through a PR here; the reusable workflow is
consumed at `@main`, so a merged change applies to every adopting repo on its
next README edit.

## License

[MIT](LICENSE)
