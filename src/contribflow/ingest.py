from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from contribflow.logging import configure_logging

logger = configure_logging()


def _record_hash(row: dict) -> str:
    raw = json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_csv_to_raw(engine: Engine, csv_path: str) -> int:
    '''
    Charge un CSV en raw.contributions_raw (append-only, dédoublonné par record_hash).
    Idempotent : rejouer le même fichier ne duplique pas les lignes.
    '''
    path = Path(csv_path)
    df = pd.read_csv(path)
    df["event_date"] = pd.to_datetime(df["event_date"], utc=False)

    ingestion_ts = datetime.now(timezone.utc)
    source_file = path.name

    records = []
    for _, r in df.iterrows():
        base = {
            "declaration_id": str(r["declaration_id"]),
            "taxpayer_id": str(r["taxpayer_id"]),
            "event_date": r["event_date"].date().isoformat(),
            "amount": float(r["amount"]),
            "currency": str(r["currency"]),
            "contribution_type": str(r["contribution_type"]),
            "status": str(r["status"]),
            "country": str(r["country"]),
        }
        rec_hash = _record_hash(base)
        records.append(
            {
                "ingestion_ts": ingestion_ts,
                "source_file": source_file,
                "record_hash": rec_hash,
                **base,
                "payload": json.dumps(base, ensure_ascii=False),
            }
        )

    insert_sql = text(
        '''
        INSERT INTO raw.contributions_raw (
            ingestion_ts, source_file, record_hash,
            declaration_id, taxpayer_id, event_date, amount, currency,
            contribution_type, status, country, payload
        )
        VALUES (
            :ingestion_ts, :source_file, :record_hash,
            :declaration_id, :taxpayer_id, :event_date, :amount, :currency,
            :contribution_type, :status, :country, CAST(:payload AS JSONB)
        )
        ON CONFLICT (record_hash) DO NOTHING
        '''
    )

    with engine.begin() as conn:
        conn.execute(insert_sql, records)
        res = conn.execute(
            text("SELECT COUNT(*) FROM raw.contributions_raw WHERE source_file=:sf"),
            {"sf": source_file},
        ).scalar_one()

    logger.info("Loaded raw file {} -> {} rows (stable count per file)", source_file, res)
    return int(res)
