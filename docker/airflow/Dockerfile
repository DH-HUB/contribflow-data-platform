FROM apache/airflow:2.9.3-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends build-essential     && apt-get clean && rm -rf /var/lib/apt/lists/*
USER airflow

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt     && pip install --no-cache-dir "dbt-core==1.8.7" "dbt-postgres>=1.8,<1.9"


ENV PYTHONPATH="/opt/contribflow/src:${PYTHONPATH}"
WORKDIR /opt/contribflow
