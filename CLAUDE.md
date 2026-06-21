# CLAUDE.md — Repo Guidance for AI Assistants

This file gives AI coding assistants (Claude, GPT, etc.) the context needed to
work effectively in **sui-agent-commerce**. Read it before touching anything.

## Project Overview

**Sui Agent Commerce** is a hackathon project for **Sui Overflow 2026 — Agentic
Web Core Track**. It demonstrates **autonomous AI agents that transact with each
other on Sui**: a buyer agent reasons about a goal, discovers a seller agent's
service, negotiates a price, pays via a policy-gated vault, and receives a
verifiable service receipt — all logged to Walrus for a tamper-evident audit trail.

The core thesis: today's agents can *think* but not *transact*. Sui's object
model makes services, payments, and receipts first-class ownable objects, which
is what unlocks agent-to-agent commerce.

## Tech Stack

| Layer | Technology |
|------|-----------|
| Language (agents) | Python 3.11 |
| LLM reasoning | Groq — Llama 3.3 70B (`llama-3.3-70b-versatile`) via OpenAI-compatible API |
| HTTP client | `httpx` (also used for Groq + Walrus) |
| On-chain logic | Sui Move (edition 2024), package `agent_commerce` |
| Audit store | Walrus testnet (publisher + aggregator REST) |
| Tests | `pytest >= 8.0` |
| Packaging | `setuptools` via `pyproject.toml` |

## Repo Layout

```
agent/                     # The Python agent runtime (the heart of the project)
  buyer.py                 # Buyer agent: LLM reasoning + rule fallback, executes purchases
  seller.py                # Seller agent: in-memory service catalog, fulfills purchases
  walrus_bridge.py         # log_agent_action / verify_action against Walrus testnet
  cli.py                   # `python -m sui_agent_commerce.cli ...` entry point
sui_agent_commerce/        # Thin package shim so `python -m sui_agent_commerce.cli` works
move/                      # Sui Move contract
  sources/commerce.move    # Service / Purchase objects, register_service / buy_service
tests/test_agent.py        # Pytest suite (services, agent decisions, Walrus round-trip)
pyproject.toml             # Project metadata + [test] extra (pytest)
```

## How to Test

```bash
# 1. Install in editable mode with the test extra
pip install -e ".[test]"

# 2. Run the suite
pytest tests/ -v
```

CI (`.github/workflows/ci.yml`) runs the exact same command on Python 3.11.

### Important: tests require network

Two tests hit the **Walrus testnet** for real:
`test_walrus_log_and_verify` and `test_full_autonomous_purchase` (which logs to
Walrus as its final step). They will fail offline or if the Walrus testnet is
down — that is expected, not a bug. Locally, make sure you have internet.

The LLM path is **optional**: if `GROQ_API_KEY` is unset, the buyer agent falls
back to deterministic keyword matching, so the agent tests pass without any key.

## How to Run the Demo

```bash
export SUI_ADDRESS=0x6dca...        # optional, for on-chain calls
export GROQ_API_KEY=gsk_...         # optional, enables LLM reasoning (else rule fallback)

python -m sui_agent_commerce.cli demo                 # full autonomous purchase flow
python -m sui_agent_commerce.cli services             # list the service catalog
python -m sui_agent_commerce.cli register-service \
  --name "BTC Price Feed" --price 500000000           # register a service (0.5 SUI = 500_000_000 mist)
python -m sui_agent_commerce.cli buy --goal "I need BTC price data" --yes
```

Prices are in **mist** (1 SUI = 1_000_000_000 mist). The code divides by `1e9` for display.

## Conventions to Respect

- **No stubs.** Code must run and tests must pass. If you add a feature, add a test.
- **Agent decisions degrade gracefully.** Always keep a non-LLM fallback path so
  the project works without API keys (see `evaluate_need`).
- **Everything an agent does gets a Walrus log.** When adding agent actions,
  route them through `walrus_bridge.log_agent_action(...)`.
- **Keep the catalog in `agent/seller.py`** consistent with what the tests assert
  (`BTC Price Feed` at `500_000_000`, ≥3 services, ≥1 in the `data` category).
- **Move package name is `agent_commerce`** (`move/Move.toml`); the module is
  `agent_commerce::commerce`. Don't rename without updating both.

## Common Tasks

| Want to... | Do this |
|-----------|---------|
| Add a service for sale | Append to `_services` in `agent/seller.py` (or use `register_service`) |
| Change the LLM model | Edit `_call_llm` in `agent/buyer.py` |
| Add an on-chain action | Add an entry fun to `move/sources/commerce.move` + emit an event |
| Bump test dep range | Edit the `test` extra in `pyproject.toml` |
