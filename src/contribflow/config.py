from __future__ import annotations

import os
from pydantic import BaseModel


class Settings(BaseModel):
    #Warehouse database
    db_host: str = os.getenv("WAREHOUSE_DB_HOST", "postgres")
    db_port: int = int(os.getenv("WAREHOUSE_DB_PORT", "5432"))
    db_name: str = os.getenv("WAREHOUSE_DB_NAME", "warehouse")
    db_user: str = os.getenv("WAREHOUSE_DB_USER", "warehouse")
    db_password: str = os.getenv("WAREHOUSE_DB_PASSWORD", "warehouse")

    data_dir: str = os.getenv("DATA_DIR", "/opt/contribflow/data")
    source_dir: str = os.getenv("SOURCE_DIR", "/opt/contribflow/data/source")

    environment: str = os.getenv("ENVIRONMENT", "local")  #local|docker|aws


settings = Settings()
