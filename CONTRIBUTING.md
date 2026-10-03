# Contributing

Thanks for helping improve OpenEval Systems Lab. The project uses synthetic fixtures and deterministic evaluation; contributions should preserve those boundaries.

## Before you start

- Check existing issues and open a focused issue for substantial changes.
- Keep changes small and explain the user or operator problem they solve.
- Do not include credentials, private data, employer code, or real customer data.
- For security vulnerabilities, follow [SECURITY.md](SECURITY.md) and report privately.

## Development setup

Use Python 3.11, Docker Compose, and Node.js 22 for the full project. Copy `.env.example` to `.env`, set a local `API_TOKEN` and `POSTGRES_PASSWORD`, then start the stack as described in [README.md](README.md).

For evaluator-only work, install the Python API requirements and run:

```bash
python -m pytest tests/unit/test_evaluator.py -q
```

Run the API integration suite against the Compose stack with `API_TOKEN` set:

```bash
API_TOKEN=your-local-token python -m pytest tests/integration -q
```

## Pull request workflow

1. Create a branch named `feat/<short-name>`, `fix/<short-name>`, or `refactor/<short-name>`.
2. Implement the smallest coherent change and add or update unit and integration tests.
3. Run the relevant checks from [README.md](README.md); note commands and outcomes in the PR.
4. Open a PR using the repository template and link the issue it resolves.
5. Address review comments in follow-up commits and keep the discussion resolved only after the change is reflected.
6. Wait for required CI checks and maintainer approval before merge.

Use conventional commit prefixes (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`). Avoid unrelated formatting or generated artifacts. See [the contribution workflow](docs/CONTRIBUTION_WORKFLOW.md) for review and release details.
