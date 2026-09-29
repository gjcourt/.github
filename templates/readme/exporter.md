<!-- readme-type: exporter -->
# name

One sentence — identical to the GitHub About description

Two to four sentences: what it measures, from where, and why that needed an
exporter.

**Status:** say what's true today — e.g. scraped by the homelab Prometheus since 2026-07.

## Why

The operational question these metrics answer, in one paragraph.

## Metrics

| Metric | Type | Labels | Meaning |
|---|---|---|---|
| `name_thing_total` | counter | `device` | What it counts |

The query that answers the Why:

```promql
rate(name_thing_total[5m])
```

## Quick start

```bash
git clone https://github.com/gjcourt/name && cd name
<run>
curl -s localhost:9100/metrics | grep ^name_
```

## Configuration

| Flag / variable | Default | Meaning |
|---|---|---|
| `--listen` | `:9100` | Metrics address |

## How it works

One paragraph: where the numbers come from and how often.

## Development

```bash
make lint   # exactly what CI runs
make test
```

## Deployment

See the [homelab runbook](https://github.com/gjcourt/homelab/blob/master/docs/operations/apps/name.md).

## License

[Apache-2.0](LICENSE)
