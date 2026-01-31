import pandas as pd
from contribflow.quality import validate

def test_quality_ok():
    df = pd.DataFrame([{
        "declaration_id": "DEC_20250101_000001",
        "taxpayer_id": "TAXP_12345",
        "event_date": "2025-01-01",
        "amount": 100.0,
        "currency": "EUR",
        "contribution_type": "INCOME_TAX",
        "status": "PAID",
        "country": "LU",
    }])
    df["event_date"] = pd.to_datetime(df["event_date"])
    ok, issues = validate(df)
    assert ok
    assert issues == []

def test_quality_fail_negative_amount():
    df = pd.DataFrame([{
        "declaration_id": "DEC_20250101_000001",
        "taxpayer_id": "TAXP_12345",
        "event_date": "2025-01-01",
        "amount": -1.0,
        "currency": "EUR",
        "contribution_type": "INCOME_TAX",
        "status": "PAID",
        "country": "LU",
    }])
    df["event_date"] = pd.to_datetime(df["event_date"])
    ok, issues = validate(df)
    assert not ok
    assert len(issues) == 1
