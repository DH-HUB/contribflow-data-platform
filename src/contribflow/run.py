from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import typer
from sqlalchemy import text

from contribflow.config import settings
from contribflow.db import init_db, make_engine
from contribflow.ingest import load_csv_to_raw
from contribflow.logging import configure_logging
from contribflow.quality import validate
from contribflow.sample_data import generate_daily_file

logger = configure_logging()
app = typer.Typer(add_completion=False)


def _write_run(
    engine,
    run_id,
    dag_id,
    task_id,
    started_at,
    status,
    source_file=None,
    rows_loaded=None,
    error_message=None,
    finished_at=None,
):
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO meta.etl_run(run_id, dag_id, task_id, started_at, finished_at, status, source_file, rows_loaded, error_message)
                VALUES (:run_id, :dag_id, :task_id, :started_at, :finished_at, :status, :source_file, :rows_loaded, :error_message)
                """
            ),
            {
                "run_id": run_id,
                "dag_id": dag_id,
                "task_id": task_id,
                "started_at": started_at,
                "finished_at": finished_at,
                "status": status,
                "source_file": source_file,
                "rows_loaded": rows_loaded,
                "error_message": error_message,
            },
        )


@app.command()
def init():
    """Initialise schemas & tables (raw/staging/marts/meta)."""
    engine = make_engine()
    init_db(engine)
    logger.info("DB initialised")


@app.command()
def generate(day: str = typer.Option(None, help="YYYY-MM-DD (default: today UTC)"), n: int = 500):
    """Génère un fichier source synthétique du jour dans data/source/."""
    engine = make_engine()
    init_db(engine)

    if day is None:
        d = datetime.now(UTC).date()
    else:
        d = pd.to_datetime(day).date()

    out_dir = settings.source_dir
    path = generate_daily_file(out_dir, d, n=n)
    logger.info("Generated {}", path)


@app.command()
def ingest(csv_path: str):
    """Charge un fichier CSV en raw (idempotent) + exécute validation Pandera."""
    engine = make_engine()
    init_db(engine)

    run_id = uuid.uuid4()
    dag_id = "manual"
    task_id = "ingest_validate"
    started_at = datetime.now(UTC)

    try:
        df = pd.read_csv(csv_path)
        df["event_date"] = pd.to_datetime(df["event_date"])
        ok, issues = validate(df)

        if not ok:
            with engine.begin() as conn:
                for issue in issues:
                    conn.execute(
                        text(
                            """
                            INSERT INTO meta.data_quality_issue(issue_id, run_id, detected_at, rule_name, severity, sample, details)
                            VALUES (:issue_id, :run_id, :detected_at, :rule_name, :severity, CAST(:sample AS JSONB), :details)
                            """
                        ),
                        {
                            "issue_id": uuid.uuid4(),
                            "run_id": run_id,
                            "detected_at": issue["detected_at"],
                            "rule_name": issue["rule_name"],
                            "severity": issue["severity"],
                            "sample": json.dumps(issue.get("sample")),
                            "details": issue.get("details"),
                        },
                    )

            _write_run(
                engine,
                run_id,
                dag_id,
                task_id,
                started_at,
                "FAILED",
                source_file=Path(csv_path).name,
                error_message="Data quality failed",
                finished_at=datetime.now(UTC),
            )
            raise typer.Exit(code=2)

        rows = load_csv_to_raw(engine, csv_path)
        _write_run(
            engine,
            run_id,
            dag_id,
            task_id,
            started_at,
            "SUCCESS",
            source_file=Path(csv_path).name,
            rows_loaded=rows,
            finished_at=datetime.now(UTC),
        )
        logger.info("Ingest SUCCESS, rows={}", rows)
    except Exception as e:
        _write_run(
            engine,
            run_id,
            dag_id,
            task_id,
            started_at,
            "FAILED",
            source_file=Path(csv_path).name,
            error_message=str(e),
            finished_at=datetime.now(UTC),
        )
        raise


if __name__ == "__main__":
    app()
