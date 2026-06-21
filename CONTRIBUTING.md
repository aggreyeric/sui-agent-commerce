# Contributing to Sui Agent Commerce

Thanks for your interest in contributing! This guide covers the basics:
installing dependencies, running tests, and the pull request workflow.

## Prerequisites

- **Python** ≥ 3.11
- **Sui CLI** (for building/testing Move packages under `move/`) — see
  https://docs.sui.io/guides/developer/getting-started/sui-install

## Installing dependencies

This project uses a standard `pyproject.toml`. We recommend an isolated
virtual environment:

```bash
git clone https://github.com/aggreyeric/sui-agent-commerce.git
cd sui-agent-commerce

# Create and activate a venv
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install the project + dev/test extras
pip install -e ".[dev]"
```

The Move package under `move/` has no extra install step — it is built with the
Sui CLI directly (see below).

## Running tests

### Python tests

```bash
pytest                    # runs everything under tests/
pytest -v                 # verbose
pytest tests/test_agent.py  # single file
```

Test discovery is configured in `pyproject.toml` (`testpaths = ["tests"]`).

### Move tests (optional)

If you have the Sui CLI installed and want to verify the on-chain package:

```bash
cd move
sui move build
sui move test
cd ..
```

## Pull request process

1. **Fork & branch.** Fork the repo and create a feature branch off `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
2. **Write code + tests.** New behavior should come with a test in `tests/`.
   Make sure the full suite passes locally:
   ```bash
   pytest
   ```
3. **Keep commits focused.** Use clear commit messages following
   [Conventional Commits](https://www.conventionalcommits.org/), e.g.
   `feat: add buyer retry logic`, `fix: walrus blob encoding`,
   `docs: clarify README`.
4. **Open a PR** against `main`. Describe:
   - What changed and why
   - How it was tested
   - Any breaking changes or follow-ups
5. **Review.** A maintainer will review. Address feedback by pushing more
   commits to the same branch (don't squash until asked).
6. **Merge.** Once approved and CI is green, a maintainer squashes & merges.

### Code style

- Python: 4-space indent, keep functions small, type-hint public APIs.
- Don't commit `.venv*/`, `__pycache__/`, or `.env` — they're in `.gitignore`.

## Reporting issues

Found a bug or have an idea? Open a GitHub Issue with:
- Expected vs. actual behavior
- Steps to reproduce
- Relevant logs / versions (Python, Sui CLI, OS)

Thanks for helping make Sui Agent Commerce better! 🚀
