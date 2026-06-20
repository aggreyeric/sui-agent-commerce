"""
Walrus bridge — every agent transaction gets logged to Walrus for verifiable audit.

This reuses the pattern from walrus-audit-vault: store the full transaction
context as a blob on Walrus, making the agent's actions tamper-evident.
"""

from __future__ import annotations

import hashlib
import json
import time
import httpx

WALRUS_PUBLISHER = "https://publisher.walrus-testnet.walrus.space/v1/blobs"
WALRUS_AGGREGATOR = "https://aggregator.walrus-testnet.walrus.space/v1/blobs"


def log_agent_action(action: dict, timeout: float = 30.0) -> str | None:
    """Log an agent action to Walrus. Returns the blob ID or None on failure.

    Args:
        action: Dict describing the action (actor, verb, target, amount, etc.)

    Returns:
        Walrus blob ID string, or None if storage failed.
    """
    # Add timestamp if not present
    action.setdefault("timestamp", int(time.time()))

    # Content hash for tamper-evidence
    canonical = json.dumps(action, sort_keys=True, separators=(",", ":")).encode("utf-8")
    content_hash = hashlib.sha256(canonical).hexdigest()
    action["content_hash"] = content_hash

    payload = json.dumps(action, sort_keys=True).encode("utf-8")

    try:
        resp = httpx.put(
            WALRUS_PUBLISHER,
            content=payload,
            headers={"Content-Type": "application/octet-stream"},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        if "newlyCreated" in data:
            return data["newlyCreated"]["blobObject"]["blobId"]
        if "alreadyCertified" in data:
            return data["alreadyCertified"]["blobId"]
        return None
    except Exception:
        return None


def verify_action(blob_id: str) -> dict | None:
    """Retrieve a logged agent action from Walrus by blob ID."""
    try:
        resp = httpx.get(f"{WALRUS_AGGREGATOR}/{blob_id}", timeout=30.0)
        resp.raise_for_status()
        return json.loads(resp.content.decode("utf-8"))
    except Exception:
        return None
