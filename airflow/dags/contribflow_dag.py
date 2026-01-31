from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PROJECT_DIR = "/opt/contribflow"
DATA_SOURCE_DIR = "/opt/airflow/data/source"


def _latest_source_file() -> str:
    p = Path(DATA_SOURCE_DIR)
    files = sorted(p.glob("contributions_*.csv"))
    if not files:
        raise FileNotFoundError("No source files found. Run generate_source first.")
    return str(files[-1])


with DAG(
    dag_id="contribflow_daily",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["portfolio", "data-engineering", "contribflow"],
) as dag:
    init_db = BashOperator(
        task_id="init_db",
        bash_command="python -m contribflow.run init",
        cwd=PROJECT_DIR,
    )

    generate_source = BashOperator(
        task_id="generate_source",
        bash_command="mkdir -p /opt/airflow/data/source && python -m contribflow.run generate --n 500",
        cwd=PROJECT_DIR,
    )

    pick_latest = PythonOperator(
        task_id="pick_latest",
        python_callable=_latest_source_file,
    )

    ingest_validate = BashOperator(
        task_id="ingest_validate",
        bash_command="python -m contribflow.run ingest \"{{ ti.xcom_pull(task_ids='pick_latest') }}\"",
        cwd=PROJECT_DIR,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "mkdir -p /opt/airflow/logs/dbt /opt/airflow/dbt_target && "
            "export DBT_TARGET_PATH=/opt/airflow/dbt_target && "
            "dbt run --project-dir /opt/contribflow/dbt --profiles-dir /opt/contribflow/dbt "
            "--log-path /opt/airflow/logs/dbt --log-format text"
        ),
        cwd=PROJECT_DIR,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "mkdir -p /opt/airflow/logs/dbt /opt/airflow/dbt_target && "
            "export DBT_TARGET_PATH=/opt/airflow/dbt_target && "
            "dbt test --project-dir /opt/contribflow/dbt --profiles-dir /opt/contribflow/dbt "
            "--log-path /opt/airflow/logs/dbt --log-format text"
        ),
        cwd=PROJECT_DIR,
    )

    init_db >> generate_source >> pick_latest >> ingest_validate >> dbt_run >> dbt_test
