# Contributing

Thanks for your interest in contributing to the Exam Card System.

Getting started

- Fork the repository and open a feature branch from `main`.
- Run the app locally (create venv, install requirements), run tests and linting before submitting PRs.

Development workflow

1. Create a topic branch: `git checkout -b feature/your-feature`.
2. Make small, focused commits with descriptive messages.
3. Run tests: `pytest -q`.
4. Push branch and open a pull request targeting `main`.

Code style and tests

- Keep code readable and well-tested. Add unit tests for new behavior.
- Follow PEP8 for Python code.

Security

- Don't commit secrets (API keys, DSNs). Use repository secrets for CI or `.env` files locally.

Contact

If you need help, open an issue on GitHub describing the problem and environment.
