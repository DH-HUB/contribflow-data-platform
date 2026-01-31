from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from contribflow.config import settings


def make_engine(url: str | None = None) -> Engine:
    if url is None:
        url = (
            f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
    return create_engine(url, pool_pre_ping=True)


DDL = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE IF NOT EXISTS raw.contributions_raw (
    ingestion_ts      TIMESTAMPTZ NOT NULL,
    source_file       TEXT NOT NULL,
    record_hash       TEXT NOT NULL,
    declaration_id    TEXT NOT NULL,
    taxpayer_id       TEXT NOT NULL,
    event_date        DATE NOT NULL,
    amount            NUMERIC(18,2) NOT NULL,
    currency          TEXT NOT NULL,
    contribution_type TEXT NOT NULL,
    status            TEXT NOT NULL,
    country           TEXT NOT NULL,
    payload           JSONB NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_raw_contributions_hash
ON raw.contributions_raw(record_hash);

CREATE TABLE IF NOT EXISTS meta.etl_run (
    run_id            UUID PRIMARY KEY,
    dag_id            TEXT NOT NULL,
    task_id           TEXT NOT NULL,
    started_at        TIMESTAMPTZ NOT NULL,
    finished_at       TIMESTAMPTZ,
    status            TEXT NOT NULL,
    source_file       TEXT,
    rows_loaded       BIGINT,
    error_message     TEXT
);

CREATE TABLE IF NOT EXISTS meta.data_quality_issue (
    issue_id          UUID PRIMARY KEY,
    run_id            UUID NOT NULL,
    detected_at       TIMESTAMPTZ NOT NULL,
    rule_name         TEXT NOT NULL,
    severity          TEXT NOT NULL,
    sample            JSONB,
    details           TEXT
);
"""


def init_db(engine: Engine) -> None:
    with engine.begin() as conn:
        for stmt in DDL.strip().split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))
