import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def test_invalid_input():
    with pytest.raises(ValueError):
        process_ticket_manifest("invalid", 0.1)


def test_negative_tax():
    with pytest.raises(ValueError):
        process_ticket_manifest([], -0.1)


def test_confirmed_and_unconfirmed():
    manifests = [
        {"is_confirmed": False, "tier": "general"},
        {"is_confirmed": True, "tier": "general",
         "orders": [{"qty": 2}]}
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result["total_revenue"] == 90.0


def test_vip_premium_general():
    manifests = [
        {"is_confirmed": True, "tier": "vip", "orders": [{"qty": 1}]},
        {"is_confirmed": True, "tier": "premium", "orders": [{"qty": 1}]},
        {"is_confirmed": True, "tier": "general", "orders": [{"qty": 1}]}
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result["total_revenue"] == 285.0


def test_unknown_tier():
    result = process_ticket_manifest([
        {"is_confirmed": True, "tier": "unknown"}
    ], 0)
    assert result["status"] == "ZERO_SALES"


def test_zero_and_negative_quantity():
    result = process_ticket_manifest([
        {"is_confirmed": True, "tier": "general",
         "orders": [{"qty": 0}, {"qty": -1}]}
    ], 0)
    assert result["status"] == "ZERO_SALES"


def test_fraud_general_and_vip():
    manifests = [
        {"is_confirmed": True, "tier": "general",
         "orders": [{"qty": 1, "promo": "FRAUD_RISK"}]},
        {"is_confirmed": True, "tier": "vip",
         "orders": [{"qty": 1, "promo": "FRAUD_RISK"}]}
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result["total_revenue"] == 45.0


def test_earlybird_and_bulk_discount():
    manifests = [{
        "is_confirmed": True,
        "tier": "general",
        "orders": [
            {"qty": 2, "promo": "EARLYBIRD"},
            {"qty": 5, "promo": ""}
        ]
    }]
    result = process_ticket_manifest(manifests, 0)
    assert result["total_revenue"] == 277.0


def test_lounge_enabled_and_disabled():
    manifests = [
        {"is_confirmed": True, "tier": "general",
         "exclusive_lounge": True, "orders": [{"qty": 1}]},
        {"is_confirmed": True, "tier": "general",
         "exclusive_lounge": False, "orders": [{"qty": 1}]}
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result["total_revenue"] == 165.0


def test_audit_rejected():
    manifests = [
        {"is_confirmed": True, "tier": "unknown"}
        for _ in range(5)
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result["status"] == "AUDIT_REJECTED"


def test_completed_status():
    result = process_ticket_manifest([
        {"is_confirmed": True, "tier": "general",
         "orders": [{"qty": 1}]}
    ], 0)
    assert result["status"] == "COMPLETED"


def test_no_data():
    assert monitor_gate_flow([]) == "NO_DATA"


def test_overflow():
    assert monitor_gate_flow([[51, 60]]) == "OVERFLOW"


def test_normal_flow():
    assert monitor_gate_flow([[40, 60, 30]]) == "FLOW_NORMAL"


def test_congestion_reset():
    assert monitor_gate_flow([[60, 40, 60]]) == "FLOW_NORMAL"


def test_multiple_streams():
    assert monitor_gate_flow([[60], [60]]) == "FLOW_NORMAL"
