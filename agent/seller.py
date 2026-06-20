"""
Seller Agent — registers services for sale on the Sui marketplace.

In a production system this would be a persistent agent process. For the
hackathon demo, this module provides functions to register services and
fulfill purchases, logging everything to Walrus.
"""

from __future__ import annotations

import json
import sys
import time

from .walrus_bridge import log_agent_action


# In-memory service catalog (in production, this reads from Sui on-chain objects)
_services: list[dict] = [
    {
        "name": "BTC Price Feed",
        "description": "Real-time BTC/USD price data, updated every 5 seconds",
        "price": 500_000_000,  # 0.5 SUI
        "seller": "0xSELLER_BTC_FEED",
        "category": "data",
        "active": True,
    },
    {
        "name": "Sentiment Analysis API",
        "description": "Analyze social media sentiment for any token",
        "price": 200_000_000,  # 0.2 SUI
        "seller": "0xSELLER_SENTIMENT",
        "category": "ai",
        "active": True,
    },
    {
        "name": "Smart Contract Audit",
        "description": "Automated security audit of a Move contract",
        "price": 5_000_000_000,  # 5 SUI
        "seller": "0xSELLER_AUDIT",
        "category": "security",
        "active": True,
    },
]


def list_services(category: str | None = None) -> list[dict]:
    """Return available services, optionally filtered by category."""
    if category:
        return [s for s in _services if s["category"] == category and s["active"]]
    return [s for s in _services if s["active"]]


def get_service(name: str) -> dict | None:
    """Find a service by name."""
    for s in _services:
        if s["name"].lower() == name.lower():
            return s
    return None


def register_service(name: str, description: str, price: int, category: str = "general") -> dict:
    """Register a new service for sale and log to Walrus."""
    service = {
        "name": name,
        "description": description,
        "price": price,
        "seller": "0xSELLER_LOCAL",
        "category": category,
        "active": True,
        "registered_at": int(time.time()),
    }
    _services.append(service)

    # Log the registration to Walrus
    blob_id = log_agent_action({
        "agent": "SellerAgent",
        "action": "register_service",
        "service": name,
        "price": price,
    })
    if blob_id:
        service["audit_blob_id"] = blob_id

    return service


def fulfill_purchase(service_name: str, buyer_address: str, price_paid: int) -> dict:
    """Fulfill a purchase — deliver the service and issue a receipt.

    Returns the receipt object (would be a Sui `Purchase` object in production).
    """
    service = get_service(service_name)
    if not service:
        return {"error": "Service not found"}

    receipt = {
        "service": service_name,
        "buyer": buyer_address,
        "seller": service["seller"],
        "price_paid": price_paid,
        "delivered_at": int(time.time()),
        "status": "DELIVERED",
    }

    # Log the fulfillment to Walrus
    blob_id = log_agent_action({
        "agent": "SellerAgent",
        "action": "fulfill_purchase",
        "service": service_name,
        "buyer": buyer_address,
        "price_paid": price_paid,
    })
    if blob_id:
        receipt["audit_blob_id"] = blob_id

    return receipt
