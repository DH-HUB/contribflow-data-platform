from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandera as pa
import pandas as pd
from pandera import Column, Check

from contribflow.logging import configure_logging

logger = configure_logging()

SCHEMA = pa.DataFrameSchema(
    {
        "declaration_id": Column(str, nullable=False, unique=True),
        "taxpayer_id": Column(str, nullable=False),
        "event_date": Column(pa.DateTime, nullable=False),
        "amount": Column(float, nullable=False, checks=Check.ge(0)),
        "currency": Column(str, nullable=False),
        "contribution_type": Column(str, nullable=False),
        "status": Column(str, nullable=False),
        "country": Column(str, nullable=False),
    },
    strict=False,
)


def validate(df: pd.DataFrame) -> tuple[bool, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    try:
        _ = SCHEMA.validate(df, lazy=True)
        return True, issues
    except pa.errors.SchemaErrors as e:
        failure = e.failure_cases
        sample = failure.head(25).to_dict(orient="records")
        issues.append(
            {
                "rule_name": "pandera_schema",
                "severity": "ERROR",
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "sample": sample,
                "details": f"{len(failure)} validation errors",
            }
        )
        logger.error("Data quality failed: {} errors", len(failure))
        return False, issues
