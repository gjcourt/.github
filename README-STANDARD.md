# README standard

How every public code repo under `gjcourt` writes its README. One skeleton,
trimmed by repo type; templates in [`templates/readme/`](templates/readme/);
structure checked in CI by [`readme-check`](#the-check).

## Principles

1. **Written for someone arriving cold.** A README answers, in this order:
   *what is this · is it real · can I try it in a minute · how do I use it ·
   how does it work · how do I work on it.* Anything else is a link.
2. **Honest status, above the fold.** One `**Status:**` line saying how real
   the project is — in daily use, experimental, hardware-confirmed on X,
   unmaintained. Claims are verified or absent: no benchmarks that weren't
   measured, no "supports X" that wasn't tried, and **every command in the
   README has been run** against the current code.
3. **One job per document.** README = meeting the project. `AGENTS.md` =
   conventions for contributors and agents. `docs/` = depth (architecture,
   runbooks, decisions). The README links to the others; it never copies
   them.
4. **Show, don't describe.** UI and CLI repos put a real screenshot or a real
   terminal transcript near the top — output that was actually produced, not
   a mock-up.
5. **No decoration.** No badges, no emoji headings, no "Table of Contents"
   (GitHub renders one). Plain Markdown that reads well as plain text.

## Skeleton

Sections appear in this order. A section a repo doesn't need is omitted, not
left empty. Headings are `##`, spelled exactly as below so the check can find
them.

```markdown
<!-- readme-type: service -->
# name

One sentence — identical to the repo's GitHub "About" description.

Two to four sentences: the problem, what this does about it, and who it's for.

**Status:** in daily use on the homelab since 2026-05.

<screenshot or terminal transcript>

## Quick start
## Usage
## Configuration
## How it works
## Development
## Deployment
## License
```

### Above the fold

| Element | Rule |
|---|---|
| `<!-- readme-type: … -->` | First line. One of the types below; tells the check which sections apply. Invisible when rendered. |
| `# name` | The repo name as written by its author (`golinks`, `toppingctl`, `Pingo`). |
| Tagline | One sentence, ≤ 120 characters, no trailing period, identical to the GitHub About description as rendered. GitHub allows 350; 120 keeps it to one sentence. |
| Pitch | 2–4 sentences. The problem first, then the answer. No "blazingly fast", "simple", "powerful". |
| `**Status:**` | Required. One line. Say what's true today and, if it matters, since when. |
| Demo | UI → screenshot in `docs/img/`, alt text required. CLI → a fenced transcript of a real run, trimmed. |

### Sections

| Section | What goes in it |
|---|---|
| **Quick start** | ≤ 5 copy-paste commands from a fresh clone to "it's running", each verified. State prerequisites in one line above the block. |
| **Usage** | The common tasks, each as a heading-less example: one sentence, one code block. Not a flag reference — link `--help` or `docs/`. |
| **Configuration** | A table: name · default · meaning. Flags or env vars, whichever the program actually reads. |
| **How it works** | One paragraph, optionally one diagram. The shape of the system, not a tour of the code. Link `docs/` for depth. |
| **Development** | Build · test · lint, **mirroring the Makefile and CI exactly** — if CI runs it, it's here, spelled the same. Point to `AGENTS.md` for conventions. |
| **Deployment** | Where it runs and how it gets there. For the homelab, a link to its runbook in `gjcourt/homelab` — don't duplicate the runbook. |
| **License** | One line naming the licence and linking `LICENSE`. |

Type-specific sections are listed with each type below.

## Types

| Type | For | Sections, in order |
|---|---|---|
| `tool` | CLIs and libraries | Quick start · Usage · Configuration · How it works · Development · License |
| `service` | Anything that runs as a server or app | Quick start · Usage · Configuration · How it works · Development · Deployment · License |
| `exporter` | Prometheus exporters and probes | Why · Metrics · Quick start · Configuration · How it works · Development · Deployment · License |
| `infra` | Monorepos, GitOps, dotfiles | Layout · Making a change · Development · License |
| `content` | Notes, lists, catalogues | Layout · Conventions · License |

**Required** in every type: the `readme-type` marker, `# name`, the tagline,
`**Status:**`, and `## License`. **Also required:** `tool`/`service` →
Quick start, Development; `exporter` → Why, Metrics, Quick start; `infra` →
Layout, Making a change; `content` → Layout. Everything else is optional but,
when present, stays in the listed order.

`exporter` extras: **Why** is the operational question the metrics answer (one
paragraph); **Metrics** is a table — name · type · labels · meaning — plus one
example PromQL query that answers the Why.

`infra` extras: **Layout** is a tree of the top-level directories with one line
each; **Making a change** is the workflow (branch, validate, PR, what deploys
it).

## Style

- Second person, present tense, active voice: "Run `make test`", not "Tests
  can be run by…".
- Code blocks are copy-paste-safe: no `$ ` prompts on commands, output shown
  in a separate block. The one exception is the demo transcript, which is a
  `text` block and not meant to be pasted.
- Relative links for anything in the repo; absolute links for other repos.
- Wrap prose at whatever the repo's editor config says; don't hard-wrap
  tables or code.
- Numbers and names over adjectives: "p95 4 ms on hestia" (if measured), not
  "very fast".

## The check

`readme-check` is a reusable workflow in this repo. A repo opts in with:

```yaml
# .github/workflows/readme.yml
name: README
on:
  pull_request:
    paths: [README.md]
  push:
    branches: [main, master]
    paths: [README.md]
jobs:
  readme:
    uses: gjcourt/.github/.github/workflows/readme-check.yml@main
```

It checks **structure, not prose**: the marker and a known type; `# name`; a
tagline of at most 120 characters that matches the GitHub About description; a
`**Status:**` line before the first section; the type's required sections
present; and every known section in order, spelled exactly. It fails with one
line per problem. It does not judge wording or accuracy — that's review's job.

## Adopting it

One PR per repo: pick the type, restructure the existing README onto the
skeleton (keep what's good — most repos already have the content, in a
different order), **run every command** before committing, set the GitHub
About description to the tagline, and add the workflow above.
