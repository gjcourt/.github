<!-- readme-type: infra -->
# name

One sentence — identical to the GitHub About description

Two to four sentences: what this repository manages and how changes reach it.

**Status:** say what's true today — e.g. source of truth for the cluster; Flux reconciles `master`.

## Layout

```text
apps/      one directory per application
infra/     controllers and cluster configuration
docs/      architecture, runbooks, plans
```

## Making a change

1. Branch from `master`.
2. Validate locally (`<command>`).
3. Open a PR; CI checks it; merging deploys it.

## Development

```bash
<the validation commands CI runs>
```

## License

[Apache-2.0](LICENSE)
