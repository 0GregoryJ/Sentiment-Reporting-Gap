import requests
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

FRED_API_KEY = os.getenv("FRED_API_KEY")

SERIES_ID = "PCE"  # Personal Consumption Expenditures (monthly)
START_DATE = "2004-01-01"

BASE_DIR = Path(__file__).resolve().parents[2]
destination_path = BASE_DIR / "data" / "raw" / "fred_api"

def fetch_fred_series_observations(series_id: str, api_key: str, start_date: str) -> pd.DataFrame:
    if not api_key:
        raise ValueError("Missing FRED_API_KEY environment variable.")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        # optional: enforce sorting, though default is fine
        "sort_order": "asc",
    }

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    obs = data.get("observations", [])
    df = pd.DataFrame(obs)

    # Transform: parse date, coerce value to numeric ('.' becomes NaN)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    df["category"] = "consumer_spending"
    df["query"] = "FRED Personal Consumption Expenditures (PCE)"
    return df

def main():
    df = fetch_fred_series_observations(SERIES_ID, FRED_API_KEY, START_DATE)

    df.to_parquet(destination_path / "FRED_raw.parquet", index=False)

    print(df)

if __name__ == "__main__":
    main()
