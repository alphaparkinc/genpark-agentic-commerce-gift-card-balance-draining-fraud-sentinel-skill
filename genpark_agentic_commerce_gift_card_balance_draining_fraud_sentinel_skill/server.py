# -*- coding: utf-8 -*-
"""MCP Server for Commerce Gift Card Balance Enumeration & Draining Sentinel Skill."""
import sys
import json
import logging
from typing import Dict, Any

from .core import GiftCardBalanceDrainingSentinel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOOLS_SCHEMA = [
    {
        "name": "detect_balance_check_anomaly",
        "description": "Analyze velocity and IP entropy of gift card balance inquiry requests to detect automated enumeration bot attacks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "requests_per_minute": {
                    "type": "integer"
                },
                "unique_ip_count": {
                    "type": "integer"
                },
                "invalid_pin_failure_rate_pct": {
                    "type": "number"
                },
                "card_prefix_sequential_score": {
                    "type": "number",
                    "description": "0.0 to 1.0"
                }
            },
            "required": [
                "requests_per_minute",
                "unique_ip_count",
                "invalid_pin_failure_rate_pct"
            ]
        }
    },
    {
        "name": "apply_protective_card_freeze",
        "description": "Lock compromised gift card ranges and enforce CAPTCHA rate limits on balance check endpoints.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "incident_id": {
                    "type": "string"
                },
                "threat_score": {
                    "type": "number"
                },
                "suspected_botnet_cidrs": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "incident_id",
                "threat_score",
                "suspected_botnet_cidrs"
            ]
        }
    }
]

def handle_rpc(line: str) -> str:
    try:
        req = json.loads(line)
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agentic-commerce-gift-card-balance-draining-fraud-sentinel-skill", "version": "1.0.0"}
            }
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": res})

        elif method == "tools/list":
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SCHEMA}})

        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            target_func = getattr(GiftCardBalanceDrainingSentinel, tool_name, None)
            if not target_func:
                return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {tool_name}"}})

            result = target_func(**args)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            })

        else:
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": req.get("id") if "req" in locals() else None, "error": {"code": -32000, "message": str(e)}})

def run_test():
    print("[TEST] Running internal RPC self-test for genpark-agentic-commerce-gift-card-balance-draining-fraud-sentinel-skill...")
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init_res = json.loads(handle_rpc(init_req))
    assert init_res.get("result", {}).get("serverInfo", {}).get("name") == "genpark-agentic-commerce-gift-card-balance-draining-fraud-sentinel-skill"

    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    list_res = json.loads(handle_rpc(list_req))
    assert len(list_res.get("result", {}).get("tools", [])) == 2
    print(f"[TEST] SUCCESS: {len(list_res['result']['tools'])} tools verified.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        if run_test():
            sys.exit(0)
        sys.exit(1)

    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
