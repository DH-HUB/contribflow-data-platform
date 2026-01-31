from __future__ import annotations

import random
from datetime import date
from pathlib import Path

import pandas as pd

CONTRIBUTION_TYPES = ["INCOME_TAX", "PROPERTY_TAX", "PENALTY", "REFUND"]
STATUSES = ["PAID", "DUE", "CANCELLED"]
CURRENCIES = ["EUR"]
COUNTRIES = ["LU", "FR", "DE", "BE"]


def generate_daily_file(output_dir: str, day: date, n: int = 500) -> Path:
    '''
    Génère un fichier CSV synthétique (données non réelles) simulant un export d'un système source.
    '''
    random.seed(int(day.strftime("%Y%m%d")))
    rows = []
    for i in range(n):
        taxpayer = f"TAXP_{random.randint(10000, 99999)}"
        declaration = f"DEC_{day.strftime('%Y%m%d')}_{i:06d}"
        amount = round(max(0, random.gauss(250, 180)), 2)
        rows.append(
            {
                "declaration_id": declaration,
                "taxpayer_id": taxpayer,
                "event_date": day.isoformat(),
                "amount": amount,
                "currency": random.choice(CURRENCIES),
                "contribution_type": random.choice(CONTRIBUTION_TYPES),
                "status": random.choices(STATUSES, weights=[0.75, 0.22, 0.03])[0],
                "country": random.choice(COUNTRIES),
            }
        )

    df = pd.DataFrame(rows)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"contributions_{day.strftime('%Y%m%d')}.csv"
    df.to_csv(path, index=False)
    return path
