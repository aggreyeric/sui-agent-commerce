"""
Buyer Agent — autonomously identifies needs, evaluates services, and purchases.

This is the core of the "Agentic Web" entry: an AI agent that REASONS about
what it needs, FINDS a service, and EXECUTES a purchase — all autonomously.

Uses Groq (Llama 3.3 70B) for reasoning. Falls back to rule-based decisions
if no API key is available.
"""

from __future__ import annotations

import json
import os
import sys
import time

from .seller import list_services, get_service, fulfill_purchase
from .walrus_bridge import log_agent_action


# ── LLM Integration ──────────────────────────────────────────

def _call_llm(prompt: str, max_tokens: int = 300) -> str | None:
    """Call Groq LLM. Returns the response text or None."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        import httpx
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are an autonomous purchasing agent. Respond ONLY with valid JSON, no markdown."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.3,
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        return None


# ── Agent Decision Logic ─────────────────────────────────────

def evaluate_need(goal: str, budget_mist: int) -> dict:
    """Given a goal and budget, decide what service to buy.

    Tries LLM reasoning first. Falls back to keyword matching.

    Returns: {service_name, reasoning, price, affordable}
    """
    services = list_services()
    catalog_str = "\n".join(
        f"- {s['name']} ({s['price'] / 1e9} SUI): {s['description']}"
        for s in services
    )

    # Try LLM-based evaluation
    prompt = f"""You are an autonomous agent with a goal and budget. Decide which service to purchase.

Goal: {goal}
Budget: {budget_mist / 1e9} SUI

Available services:
{catalog_str}

Respond with JSON only:
{{"chosen": "service name", "reasoning": "why", "affordable": true/false}}"""

    llm_response = _call_llm(prompt)
    if llm_response:
        try:
            # Strip markdown code fences if present
            clean = llm_response.strip().strip("`").strip()
            if clean.startswith("json"):
                clean = clean[4:].strip()
            decision = json.loads(clean)
            # Validate against catalog
            chosen = get_service(decision.get("chosen", ""))
            if chosen:
                decision["price"] = chosen["price"]
                decision["affordable"] = chosen["price"] <= budget_mist
                decision["method"] = "llm"
                return decision
        except (json.JSONDecodeError, KeyError):
            pass  # fall through to rule-based

    # Fallback: rule-based keyword matching
    goal_lower = goal.lower()
    for s in services:
        keywords = s["name"].lower() + " " + s["description"].lower() + " " + s["category"]
        if any(w in goal_lower for w in keywords.split()):
            return {
                "chosen": s["name"],
                "reasoning": f"Keyword match: service '{s['name']}' aligns with goal",
                "price": s["price"],
                "affordable": s["price"] <= budget_mist,
                "method": "rule_based",
            }

    # Ultimate fallback: cheapest affordable
    affordable = [s for s in services if s["price"] <= budget_mist]
    if affordable:
        cheapest = min(affordable, key=lambda s: s["price"])
        return {
            "chosen": cheapest["name"],
            "reasoning": "Fallback: cheapest affordable service",
            "price": cheapest["price"],
            "affordable": True,
            "method": "fallback",
        }

    return {"chosen": None, "reasoning": "No affordable services", "affordable": False, "method": "none"}


def execute_purchase(
    goal: str,
    buyer_address: str = "0xBUYER_AGENT",
    budget_mist: int = 1_000_000_000,  # 1 SUI
    auto_confirm: bool = False,
) -> dict:
    """Full autonomous purchase flow: evaluate → confirm → buy → log.

    This is the main agent entry point. Returns the full transaction record.
    """
    print(f"\n🤖 Buyer Agent activated")
    print(f"   Goal: {goal}")
    print(f"   Budget: {budget_mist / 1e9} SUI")
    print(f"   Address: {buyer_address}")
    print()

    # Step 1: Evaluate need
    print("   [1/4] Evaluating services...")
    decision = evaluate_need(goal, budget_mist)
    method_tag = f" ({decision['method']})" if "method" in decision else ""
    print(f"   → Chose: {decision.get('chosen')}{method_tag}")
    print(f"   → Reason: {decision.get('reasoning')}")

    if not decision.get("chosen") or not decision.get("affordable"):
        print(f"   ❌ Cannot proceed: {'not affordable' if decision.get('chosen') else 'no match'}")
        return {"status": "aborted", "reason": decision.get("reasoning")}

    # Step 2: Confirm (auto or prompt)
    if not auto_confirm:
        print(f"\n   [2/4] Proposed purchase: {decision['chosen']} for {decision['price'] / 1e9} SUI")
        print(f"   ⏎ Auto-confirming (demo mode)...")

    # Step 3: Execute purchase
    print(f"   [3/4] Executing purchase...")
    receipt = fulfill_purchase(decision["chosen"], buyer_address, decision["price"])
    if "error" in receipt:
        print(f"   ❌ Purchase failed: {receipt['error']}")
        return {"status": "failed", **receipt}

    print(f"   ✅ Purchased: {receipt['service']}")
    print(f"   📄 Receipt delivered")

    # Step 4: Log to Walrus
    print(f"   [4/4] Logging transaction to Walrus...")
    blob_id = log_agent_action({
        "agent": "BuyerAgent",
        "action": "autonomous_purchase",
        "goal": goal,
        "service": decision["chosen"],
        "price_paid": decision["price"],
        "buyer": buyer_address,
        "reasoning": decision.get("reasoning"),
        "receipt_delivered": True,
    })

    result = {
        "status": "completed",
        "goal": goal,
        "service_purchased": decision["chosen"],
        "price_paid": decision["price"],
        "reasoning": decision.get("reasoning"),
        "method": decision.get("method"),
        "receipt": receipt,
        "audit_blob_id": blob_id,
    }

    if blob_id:
        print(f"   🦭 Audit log stored on Walrus: {blob_id}")
    print(f"\n   ✅ Autonomous purchase complete!\n")
    return result
