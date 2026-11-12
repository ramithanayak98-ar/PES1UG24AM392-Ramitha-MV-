import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


def test_general_ticket():
    manifests = [{
        "is_confirmed": True,
        "tier": "general",
        "orders": [{"qty": 2, "promo": ""}]
    }]
    result = process_ticket_manifest(manifests, 0.1)
    assert result["total_revenue"] == 99.0
    assert result["status"] == "COMPLETED"


def test_invalid_manifests():
    with pytest.raises(ValueError):
        process_ticket_manifest("invalid", 0.1)


def test_negative_tax():
    with pytest.raises(ValueError):
        process_ticket_manifest([], -0.1)


def test_unconfirmed_manifest():
    result = process_ticket_manifest([
        {"is_confirmed": False, "tier": "general"}
    ], 0)
    assert result["status"] == "ZERO_SALES"


def test_all_ticket_tiers():
    manifests = [
        {"is_confirmed": True, "tier": "vip", "orders": [{"qty": 2}]},
        {"is_confirmed": True, "tier": "premium", "orders": [{"qty": 2}]},
        {"is_confirmed": True, "tier": "general", "orders": [{"qty": 2}]}
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result["total_revenue"] == 570.0
    assert result["status"] == "COMPLETED"


def test_unknown_tier():
    result = process_ticket_manifest([
        {"is_confirmed": True, "tier": "student",
         "orders": [{"qty": 2}]}
    ], 0)
    assert result["status"] == "ZERO_SALES"


def test_invalid_quantity():
    result = process_ticket_manifest([
        {"is_confirmed": True, "tier": "general",
         "orders": [{"qty": 0}, {"qty": -2}]}
    ], 0)
    assert result["status"] == "ZERO_SALES"


def test_promo_codes_and_lounge():
    manifests = [{
        "is_confirmed": True,
        "tier": "general",
        "exclusive_lounge": True,
        "orders": [
            {"qty": 2, "promo": "FRAUD_RISK"},
            {"qty": 2, "promo": "EARLYBIRD"},
            {"qty": 5, "promo": ""},
            {"qty": 4, "promo": ""}
        ]
    }]
    result = process_ticket_manifest(manifests, 0.1)
    assert result["total_revenue"] == 684.2
    assert result["status"] == "COMPLETED"


def test_vip_fraud():
    manifests = [{
        "is_confirmed": True,
        "tier": "vip",
        "exclusive_lounge": True,
        "orders": [
            {"qty": 2, "promo": ""},
            {"qty": 1, "promo": "FRAUD_RISK"}
        ]
    }]
    result = process_ticket_manifest(manifests, 0)
    assert result["total_revenue"] == 75.0


def test_audit_rejected():
    manifests = [
        {"is_confirmed": True, "tier": "unknown"}
        for _ in range(5)
    ]
    result = process_ticket_manifest(manifests, 0)
    assert result["status"] == "AUDIT_REJECTED"


def test_zero_sales():
    result = process_ticket_manifest([
        {"is_confirmed": True, "tier": "general", "orders": []}
    ], 0)
    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_SALES"


def test_no_gate_data():
    assert monitor_gate_flow([]) == "NO_DATA"


def test_gate_overflow():
    assert monitor_gate_flow([[51, 60]]) == "OVERFLOW"


def test_gate_normal():
    assert monitor_gate_flow([[60, 40, 55]]) == "FLOW_NORMAL"


def test_gate_multiple_streams():
    assert monitor_gate_flow([[60], [55]]) == "FLOW_NORMAL"
