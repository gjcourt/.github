<!-- readme-type: service -->
# name

One sentence — identical to the GitHub About description

Two to four sentences: the problem, what this does about it, and who it's for.

**Status:** say what's true today — e.g. running on the homelab since 2026-03.

![What the main screen looks like](docs/img/screenshot.png)

## Quick start

Needs: <runtime + version>.

```bash
git clone https://github.com/gjcourt/name && cd name
<run with in-memory / local defaults>
```

Then open <http://localhost:8080>.

## Usage

The one thing most people come here to do, as an example.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `PORT` | `8080` | Listen port |

## How it works

One paragraph (and optionally one diagram) on the shape of the system. Depth
lives in [docs/](docs/).

## Development

```bash
make lint   # exactly what CI runs
make test
```

Conventions for contributors and agents: [AGENTS.md](AGENTS.md).

## Deployment

Runs on the homelab — see the
[runbook](https://github.com/gjcourt/homelab/blob/master/docs/operations/apps/name.md).

## License

[Apache-2.0](LICENSE)
