"""
CLI for Sui Agent Commerce — autonomous agent marketplace.

Usage:
  python -m sui_agent_commerce.cli demo           # Full autonomous purchase flow
  python -m sui_agent_commerce.cli services       # List available services
  python -m sui_agent_commerce.cli buy --goal "I need BTC price data"
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Make `agent` importable when run as `python -m sui_agent_commerce.cli`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.seller import list_services, register_service
from agent.buyer import execute_purchase


def cmd_demo(args):
    """Run the full autonomous agent demo."""
    print("=" * 64)
    print("  🤖 SUI AGENT COMMERCE — AUTONOMOUS PURCHASE DEMO")
    print("  Built for Sui Overflow 2026 — Agentic Web Track")
    print("=" * 64)

    # Scenario: a trading agent needs price data
    result = execute_purchase(
        goal="I need real-time BTC price data for my trading strategy",
        buyer_address="0xBUYER_AGENT_0x6dca",
        budget_mist=1_000_000_000,  # 1 SUI
        auto_confirm=True,
    )

    print("=" * 64)
    print("  RESULT")
    print("=" * 64)
    print(json.dumps(result, indent=2))

    if result.get("audit_blob_id"):
        print()
        print("  ✔ Full transaction logged on Walrus (decentralized, tamper-evident)")
        print(f"  ✔ Blob ID: {result['audit_blob_id']}")
    if result.get("method") == "llm":
        print("  ✔ Purchase decision made by LLM (Llama 3.3 70B via Groq)")
    else:
        print(f"  ✔ Purchase decision made by {result.get('method', 'fallback')} logic")


def cmd_services(args):
    """List available services."""
    services = list_services(args.category)
    print(f"\n  📦 {len(services)} services available:")
    for s in services:
        print(f"    • {s['name']} — {s['price'] / 1e9} SUI")
        print(f"      {s['description']}")
        print(f"      Category: {s['category']}")
        print()


def cmd_buy(args):
    """Execute an autonomous purchase."""
    result = execute_purchase(
        goal=args.goal,
        buyer_address=args.address or "0xBUYER_AGENT",
        budget_mist=args.budget,
        auto_confirm=args.yes,
    )
    print(json.dumps(result, indent=2))


def cmd_register(args):
    """Register a service for sale."""
    service = register_service(args.name, args.description, args.price, args.category)
    print(f"\n  ✅ Registered: {service['name']} for {service['price'] / 1e9} SUI")
    if "audit_blob_id" in service:
        print(f"  🦭 Logged on Walrus: {service['audit_blob_id']}")


def main():
    parser = argparse.ArgumentParser(description="Sui Agent Commerce CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("demo", help="Run full autonomous purchase demo").set_defaults(func=cmd_demo)
    sub.add_parser("services", help="List available services").set_defaults(func=cmd_services)

    p_buy = sub.add_parser("buy", help="Execute an autonomous purchase")
    p_buy.add_argument("--goal", required=True, help="What the agent needs")
    p_buy.add_argument("--budget", type=int, default=1_000_000_000, help="Budget in mist")
    p_buy.add_argument("--address", default=None, help="Buyer Sui address")
    p_buy.add_argument("--yes", "-y", action="store_true", help="Auto-confirm")
    p_buy.set_defaults(func=cmd_buy)

    p_reg = sub.add_parser("register-service", help="Register a service for sale")
    p_reg.add_argument("--name", required=True)
    p_reg.add_argument("--description", required=True)
    p_reg.add_argument("--price", type=int, required=True, help="Price in mist")
    p_reg.add_argument("--category", default="general")
    p_reg.set_defaults(func=cmd_register)

    # Add category filter to services
    for action in parser._subparsers._group_actions:
        for choice, subparser in action.choices.items():
            if choice == "services":
                subparser.add_argument("--category", default=None)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
