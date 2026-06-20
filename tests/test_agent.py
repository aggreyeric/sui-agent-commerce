"""Tests for Sui Agent Commerce — agent logic and Walrus integration."""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.seller import list_services, get_service, register_service, fulfill_purchase
from agent.buyer import evaluate_need, execute_purchase
from agent.walrus_bridge import log_agent_action, verify_action


def test_list_services():
    """Services catalog loads correctly."""
    services = list_services()
    assert len(services) >= 3
    names = [s["name"] for s in services]
    assert "BTC Price Feed" in names


def test_filter_by_category():
    """Category filter works."""
    data_services = list_services("data")
    assert all(s["category"] == "data" for s in data_services)
    assert len(data_services) >= 1


def test_get_service():
    """Find service by name."""
    service = get_service("BTC Price Feed")
    assert service is not None
    assert service["price"] == 500_000_000


def test_register_service():
    """Register a new service."""
    service = register_service(
        name="Test Service",
        description="For testing",
        price=100_000_000,
        category="test",
    )
    assert service["name"] == "Test Service"
    assert service["active"] is True
    found = get_service("Test Service")
    assert found is not None


def test_evaluate_need_keyword():
    """Rule-based evaluation matches keywords."""
    decision = evaluate_need("I need BTC price data", 1_000_000_000)
    assert decision["chosen"] is not None
    assert decision["affordable"] is True


def test_evaluate_need_budget_limit():
    """Agent respects budget constraints."""
    # Budget too low for anything (1 mist = effectively zero)
    decision = evaluate_need("I need an expensive audit", 1)  # 0.000000001 SUI
    assert decision["affordable"] is False or decision["chosen"] is None


def test_fulfill_purchase():
    """Purchase fulfillment issues a receipt."""
    receipt = fulfill_purchase("BTC Price Feed", "0xBUYER", 500_000_000)
    assert receipt["status"] == "DELIVERED"
    assert receipt["buyer"] == "0xBUYER"
    assert receipt["price_paid"] == 500_000_000


def test_walrus_log_and_verify():
    """Walrus integration: log an action and verify it round-trips."""
    blob_id = log_agent_action({
        "agent": "TestAgent",
        "action": "test_action",
        "test": True,
    })
    assert blob_id is not None, "Walrus storage failed"

    retrieved = verify_action(blob_id)
    assert retrieved is not None, "Walrus retrieval failed"
    assert retrieved["agent"] == "TestAgent"
    assert retrieved["action"] == "test_action"


def test_full_autonomous_purchase():
    """End-to-end: agent evaluates, buys, logs to Walrus."""
    result = execute_purchase(
        goal="I need real-time BTC price data",
        buyer_address="0xTEST_BUYER",
        budget_mist=1_000_000_000,
        auto_confirm=True,
    )
    assert result["status"] == "completed"
    assert result["service_purchased"] is not None
    assert result["audit_blob_id"] is not None
