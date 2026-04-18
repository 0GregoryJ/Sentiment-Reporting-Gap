import requests
from datetime import datetime, timezone
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
destination_path = BASE_DIR / "data" / "raw" / "bls_api"

SERIES_IDS = [
    "LNS13000000",
    "LNS14000000",
    "CES0000000001",
    "CES0500000002",
    "CES0500000003",
    "CIU2020000000000A",
]

STARTYEAR = 2004
ENDYEAR = 2026
BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

def fetch_bls_chunk(series_ids, startyear, endyear):
    headers = {"Content-type": "application/json"}
    payload = {
        "seriesid": series_ids,
        "startyear": str(startyear),
        "endyear": str(endyear),
    }

    r = requests.post(BLS_URL, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()

    status = data.get("status")
    if status and status != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API status={status} message={data.get('message')}")

    return data

def fetch_bls_all(series_ids, startyear, endyear, chunk_size=10):
    all_series = {}

    for chunk_start in range(startyear, endyear + 1, chunk_size):
        chunk_end = min(chunk_start + chunk_size - 1, endyear)
        data = fetch_bls_chunk(series_ids, chunk_start, chunk_end)

        for series in data["Results"]["series"]:
            sid = series["seriesID"]
            all_series.setdefault(sid, []).extend(series.get("data", []))

    return {
        "Results": {
            "series": [
                {"seriesID": sid, "data": vals}
                for sid, vals in all_series.items()
            ]
        }
    }

def parse_rows(bls_json, monthly_only=True):
    now = datetime.now(timezone.utc)
    rows = []

    for series in bls_json["Results"]["series"]:
        series_id = series["seriesID"]

        for item in series.get("data", []):
            period = item["period"]

            if monthly_only and not ("M01" <= period <= "M12"):
                continue

            val = item["value"]
            if val == "-":
                continue

            footnotes = ",".join(
                fn["text"] for fn in item.get("footnotes", [])
                if fn and fn.get("text")
            )

            rows.append({
                "series_id": series_id,
                "year": int(item["year"]),
                "period": period,
                "value": float(val),
                "footnotes": footnotes,
                "retrieved_at": now,
            })

    return rows

bls_json = fetch_bls_all(SERIES_IDS, STARTYEAR, ENDYEAR, chunk_size=10)
rows = parse_rows(bls_json)

BLS_data = pd.DataFrame(rows)

BLS_data["month_num"] = BLS_data["period"].str.replace("M", "", regex=False).astype(int)
BLS_data["date"] = pd.to_datetime(
    dict(year=BLS_data["year"], month=BLS_data["month_num"], day=1)
)

BLS_data = BLS_data.drop(columns=["month_num", "year", "period", "footnotes", "retrieved_at"])
BLS_data = BLS_data.rename(columns={"series_id": "query"})
BLS_data["category"] = "labor_market"

# remove duplicates in case chunk boundaries overlap
BLS_data = BLS_data.drop_duplicates(subset=["query", "date"]).sort_values(["query", "date"])

BLS_data.to_parquet(destination_path / "bls_raw.parquet", index=False)
print(BLS_data.sort_values("date"))