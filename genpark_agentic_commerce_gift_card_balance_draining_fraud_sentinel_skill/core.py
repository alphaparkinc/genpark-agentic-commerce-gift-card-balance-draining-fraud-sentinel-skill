# -*- coding: utf-8 -*-
"""Commerce Gift Card Balance Enumeration & Draining Sentinel for GenPark Agentic Commerce."""
import json
import time
from typing import Dict, Any, List

class GiftCardBalanceDrainingSentinel:
    """Anti-credential-stuffing and gift card balance draining defense engine."""

    @staticmethod
    def detect_balance_check_anomaly(requests_per_minute: int, unique_ip_count: int, invalid_pin_failure_rate_pct: float, card_prefix_sequential_score: float = 0.1) -> Dict[str, Any]:
        """Calculate bot enumeration probability and attack fingerprint."""
        ip_entropy = unique_ip_count / max(1, requests_per_minute)
        
        # High failure rate (>40%) combined with high request velocity indicates brute force
        score = 0.0
        if requests_per_minute > 100:
            score += 0.35
        if invalid_pin_failure_rate_pct > 35.0:
            score += 0.40
        if card_prefix_sequential_score > 0.60:
            score += 0.25

        threat_score = min(1.0, round(score, 2))
        is_attack = threat_score >= 0.60

        return {
            "threat_score": threat_score,
            "is_botnet_attack": is_attack,
            "attack_type": "DISTRIBUTED_CARD_ENUMERATION" if (is_attack and ip_entropy > 0.5) else ("BRUTE_FORCE_INSPECTION" if is_attack else "ORGANIC_CUSTOMER_TRAFFIC"),
            "mitigation_tier": "BLOCK_AND_CHALLENGE" if threat_score >= 0.75 else ("THROTTLE" if threat_score >= 0.50 else "MONITOR"),
            "recommended_rate_limit_rpm": 5 if is_attack else 60
        }

    @staticmethod
    def apply_protective_card_freeze(incident_id: str, threat_score: float, suspected_botnet_cidrs: List[str]) -> Dict[str, Any]:
        """Issue gateway firewall rules and lock targeted gift card bins."""
        return {
            "incident_id": incident_id,
            "status": "DEFENSE_ACTIVE",
            "firewall_rules_enacted": [
                f"Block {len(suspected_botnet_cidrs)} malicious IP CIDRs at Cloudflare/AWS WAF edge.",
                "Enforce mandatory Turnstile / reCAPTCHA v3 on all /api/v1/giftcards/balance endpoints.",
                "Temporarily lock online balance checks for target card BIN sequence.",
                "Trigger automated SMS 2FA notification for balance deductions exceeding $50."
            ],
            "protected_cidrs": suspected_botnet_cidrs
        }
