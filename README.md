# Sentiment-Reporting-Gap

Measure the gap between public economic sentiment (Google search behavior) and official macroeconomic reporting (FRED, BLS) with a Python ETL pipeline, DuckDB + SQL modeling workflow, and Streamlit dashboard.

The analytics layer applies z-score normalization and CDF-approximated sigmoid scaling to convert heterogeneous time series into comparable 0-100 sentiment indices and gap metrics, refreshed biweekly via Airflow.

## Project Layout

- `src/extract/`: API extraction scripts (FRED, BLS, SerpAPI/Google Trends).
- `sql/staging/`: raw-to-staging model SQL.
- `sql/marts/`: dimensional and fact model SQL.
- `sql/analytics/`: final feature models used by the dashboard.
- `scripts/run_local_pipeline`: runs all SQL models in order against DuckDB.
- `dashboard/`: Streamlit app, query SQL, and chart components.
- `data/`: raw parquet outputs and DuckDB file (`data/database/analytics.duckdb`).
- `airflow/dags/`: Airflow DAG for scheduled pipeline runs and data sync/push.

## Data Flow

1. Extraction scripts write raw API data to `data/raw/*/*.parquet`.
2. SQL pipeline builds staged, mart, and analytics tables in `analytics.duckdb`.
3. Dashboard queries analytics features from DuckDB.
4. Airflow DAG runs the same pipeline every 2 weeks and pushes refreshed `data/` changes.

## Requirements

- Python 3.9+ recommended
- `pip`
- Git configured for this repository
- API keys in `.env` at repo root:
  - `FRED_API_KEY`
  - `SERP_API_KEY`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Local Run (Manual)

Run extraction:

```bash
python src/extract/extract_FRED_data.py
python src/extract/extract_BLS_data.py
python src/extract/extract_SERP_data.py
```

Run SQL pipeline:

```bash
python scripts/run_local_pipeline
```

Run dashboard:

```bash
streamlit run dashboard/dashboard.py
```

## Airflow Orchestration

Main DAG:

- `airflow/dags/sentiment_reporting_gap_dag.py`
- DAG ID: `sentiment_reporting_gap_biweekly`
- Schedule: every 2 weeks
- `catchup=False`

The DAG runs:

1. `extract_FRED_data.py`
2. `extract_BLS_data.py`
3. `extract_SERP_data.py`
4. `scripts/run_local_pipeline`
5. `rsync` local data source into repo `data/`
6. `git add data && git commit && git push origin main` (if changes exist)

Supported environment overrides:

- `LOCAL_DATA_SOURCE` (default: `<repo>/data`)
- `PIPELINE_PYTHON_BIN` (default: `python`)
- `PIPELINE_GIT_SSH_KEY_PATH` (default: `~/.ssh/airflow_github`)

## Airflow UI (Current Local Setup)

If you are using the local setup created for this repo:

- URL: [http://localhost:8080](http://localhost:8080)
- Username: `admin`
- Password: `admin`

Services are started from project-local resources:

- Virtualenv: `.venv-airflow/`
- Airflow home: `.airflow-home/`

## Notes

- Dashboard query files live in `dashboard/queries/`.
- DuckDB access helper is in `dashboard/utils/db.py`.
- The DAG is configured to push to `main`, matching the current repo workflow.
