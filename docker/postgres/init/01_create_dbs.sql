DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'airflow') THEN
    CREATE ROLE airflow LOGIN PASSWORD 'airflow';
  END IF;
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'warehouse') THEN
    CREATE ROLE warehouse LOGIN PASSWORD 'warehouse';
  END IF;
END $$;

CREATE DATABASE airflow OWNER airflow;
CREATE DATABASE warehouse OWNER warehouse;
