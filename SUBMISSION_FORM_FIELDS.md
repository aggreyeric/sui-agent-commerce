# SUBMISSION_FORM_FIELDS.md — Sui Overflow 2026

Pre-filled fields for the **Devpost submission form** for *Sui Agent Commerce*.
Copy/paste-ready. Track: **Agentic Web Core**. Prize pool: **$500K**.

> Fill bracketed `[...]` placeholders before submitting. Anything marked *(Devpost)*
> maps directly to a Devpost form field.

---

## (Devpost) Project Name
Sui Agent Commerce

## (Devpost) Short Description / Tagline
Autonomous AI agents that buy and sell services from each other on Sui — using
Sui's object model for payments, service contracts, and verifiable receipts.

## (Devpost) One-Sentence Pitch
AI agents can think, but they can't transact — Sui Agent Commerce gives them a
wallet and a marketplace so one agent can autonomously buy a service from another.

## The Problem
Modern AI agents can recommend, summarize, and analyze — but they cannot
autonomously *pay* for a service, *hire* another agent, or *receive* proof of
purchase. There is no native "commerce layer" for the agentic web. Every
transaction still requires a human to pull out a credit card or sign a wallet.

## The Solution
A buyer agent reasons about its goal, discovers a seller agent's service in an
on-chain registry, receives a quote, pays via a policy-gated vault using real
SUI, and receives a transferable **Purchase** receipt object as proof. Every
step is logged to Walrus for a tamper-evident audit trail. No human in the loop.

## How We Built It
- **Buyer agent** (`agent/buyer.py`): uses Groq-hosted **Llama 3.3 70B** to reason
  about a goal and budget, evaluate the service catalog, and decide what to buy —
  with a deterministic keyword fallback when no API key is present.
- **Seller agent** (`agent/seller.py`): registers services, handles purchase
  requests, and issues receipts.
- **Sui Move contract** (`move/sources/commerce.move`, package `agent_commerce`):
  `Service` objects (what's for sale), `Purchase` receipt objects (transferable
  proof of payment), and `register_service` / `buy_service` entry functions with
  price-gated payments and on-chain events.
- **Walrus integration** (`agent/walrus_bridge.py`): every agent action is hashed
  and stored as a blob on Walrus testnet, making the full transaction history
  verifiable and immutable.

## How It Uses Sui's Object Model
- **`Service`** — a shared object representing a unit for sale, owned/registered by
  a seller agent.
- **`Purchase`** — a keyed, transferable receipt object proving an agent paid for a
  service. Because it's an object, it can be passed to other agents or contracts as
  proof-of-purchase.
- **Payments** are real `Coin<SUI>` flowing through the contract, gated by
  price assertions (`EInsufficientPayment`).
- Every commerce primitive (the thing sold, the payment, the receipt) is a
  first-class, ownable Sui object — not a database row.

## Built With (Devpost "Built With" tags)
`sui`, `sui-move`, `walrus`, `python`, `groq`, `llama`, `ai-agents`,
`autonomous-agents`, `llm`, `httpx`, `pytest`, `github-actions`

## Challenges We Ran Into
- [Describe the hardest engineering problem — e.g. mapping agent intent to an
  on-chain service object, handling LLM output unreliability for purchase
  decisions, Walrus blob lifecycle (newlyCreated vs alreadyCertified).]
- Designing a purchase-receipt as a transferable object rather than an event log.

## Accomplishments That We're Proud Of
- A fully autonomous end-to-end purchase: agent reasons → quotes → pays →
  receives a verifiable receipt → audit logged to Walrus.
- Graceful LLM fallback so the system demonstrably works with zero API keys.

## What We Learned
- [1–3 concrete takeaways about Sui object dynamics, Walrus storage, or agentic
  payments.]

## What's Next
- Persistent on-chain service registry (today the catalog is in-memory for the
  demo; wire it fully to `Service` objects).
- Multi-agent marketplaces with reputation objects.
- Policy-gated vaults enforced on-chain (the policy layer today lives off-chain).

## Links
- **GitHub repo:** https://github.com/aggreyeric/sui-agent-commerce
- **Live demo / video:** [add YouTube or demo URL]
- **Deployed Move package:** [add `0x...` package ID after `sui client publish`]

## Team
- [Team name / member names and roles]

## License
MIT
