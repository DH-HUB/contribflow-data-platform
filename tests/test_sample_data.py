from datetime import date
import pandas as pd
from contribflow.sample_data import generate_daily_file

def test_generate_daily_file(tmp_path):
    path = generate_daily_file(str(tmp_path), date(2025, 1, 1), n=10)
    df = pd.read_csv(path)
    assert len(df) == 10
    assert "declaration_id" in df.columns
