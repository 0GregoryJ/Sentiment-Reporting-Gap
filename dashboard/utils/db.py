from pathlib import Path
import duckdb
import pandas as pd

DB_PATH = Path("data/database/analytics.duckdb")


def run_query(sql: str, params: list | tuple | None = None) -> pd.DataFrame:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB file not found at {DB_PATH}. Run your pipeline first."
        )

    con = duckdb.connect(DB_PATH, read_only=True)

    try:
        if params:
            result = con.execute(sql, params).df()
        else:
            result = con.execute(sql).df()
    finally:
        con.close()

    return result