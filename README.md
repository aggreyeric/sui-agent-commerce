# 🤖 Sui Agent Commerce — Autonomous Agents That Buy & Sell on Sui

**Built for [Sui Overflow 2026 — Agentic Web Core Track](https://overflow.sui.io)**

Autonomous AI agents that can **purchase services from each other** using Sui's object model. An agent identifies a need, negotiates with a seller agent, pays via a policy-gated vault, and receives a verifiable service receipt — all on-chain, all autonomous.

> This is the **Agentic Web**: agents that act, transact, and coordinate using Sui's composable object model. No human in the loop.

## 🎯 The Problem

Today's AI agents can *think* but not *transact*. They can recommend, summarize, and analyze — but they can't autonomously buy a service, pay for data, or hire another agent. Sui's object model changes this: payments, service contracts, and receipts are all first-class objects that agents can own, transfer, and verify.

## 🏗️ What It Does

```
┌─────────────────┐         ┌─────────────────┐
│  Buyer Agent     │         │  Seller Agent    │
│  (needs data)    │         │  (has API)       │
└────────┬────────┘         └────────┬────────┘
         │                            │
         │   1. Discover service       │
         │ ──────────────────────────►│
         │                            │
         │   2. Quote: 0.5 SUI         │
         │ ◄──────────────────────────│
         │                            │
         │   3. Pay via vault          │
         │      (policy-gated)         │
         │ ──────┐                     │
         │       │ Sui tx              │
         │       ▼                     │
         │   ┌─────────┐               │
         │   │  Vault   │  4. Transfer │
         │   │ (policies)│ ───────────►│
         │   └─────────┘               │
         │                            │
         │   5. Service receipt (obj)  │
         │ ◄──────────────────────────│
         │                            │
         │   6. Audit log on Walrus   │
         │ ──────┐                     │
         │       ▼                     │
         │   ┌─────────┐               │
         │   │ Walrus  │               │
         │   │ (blob)  │               │
         │   └─────────┘               │
```

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Set up
export SUI_ADDRESS=0x6dca...
export GROQ_API_KEY=gsk_...

# Run a demo: buyer agent purchases a "price feed" service
python -m sui_agent_commerce.cli demo

# Register a service for sale
python -m sui_agent_commerce.cli register-service \
  --name "BTC Price Feed" \
  --price 500000000  # 0.5 SUI

# Browse available services
python -m sui_agent_commerce.cli services
```

## 📦 Modules

### `agent/buyer.py` — Buyer Agent
Uses an LLM (Groq) to identify needs, evaluate quotes, and execute policy-gated purchases.

### `agent/seller.py` — Seller Agent
Registers services for sale, handles purchase requests, issues verifiable receipts.

### `move/sources/commerce.move` — On-Chain Service Registry
Sui Move contract: `Service` objects (what's for sale), `Purchase` objects (receipts), and the marketplace logic.

### `agent/walrus_bridge.py` — Audit Integration
Logs every agent transaction to Walrus for verifiable, tamper-evident audit trails.

## 🎯 Why This Fits Agentic Web

| Requirement | How We Deliver |
|------------|----------------|
| Autonomous AI agents | Buyer + seller agents, LLM-driven decisions |
| Act on Sui | Payments via policy-gated vault objects |
| Transact | Real SUI transfers between agents |
| Coordinate | Service discovery + quote negotiation |
| Object model | Services, purchases, receipts are all Sui objects |

## License
MIT
