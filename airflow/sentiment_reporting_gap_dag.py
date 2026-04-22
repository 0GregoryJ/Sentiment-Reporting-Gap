from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator


REPO_ROOT = Path("/Users/gregoryjoshua/Desktop/Projects/Sentiment-Reporting-Gap")
LOCAL_DATA_SOURCE = os.getenv("LOCAL_DATA_SOURCE", str(REPO_ROOT / "data"))
REPO_DATA_DIR = str(REPO_ROOT / "data")
PYTHON_BIN = os.getenv("PIPELINE_PYTHON_BIN", "python")
GIT_SSH_KEY_PATH = os.getenv("PIPELINE_GIT_SSH_KEY_PATH", os.path.expanduser("~/.ssh/airflow_github"))


default_args = {
    "owner": "gregoryjoshua",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}


with DAG(
    dag_id="sentiment_reporting_gap_biweekly",
    description="Biweekly refresh of extraction, SQL pipeline, and GitHub data sync",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=timedelta(weeks=2),
    catchup=False,
    max_active_runs=1,
    tags=["sentiment", "duckdb", "biweekly"],
) as dag:
    extract_fred = BashOperator(
        task_id="extract_fred_data",
        cwd=str(REPO_ROOT),
        bash_command=f"{PYTHON_BIN} src/extract/extract_FRED_data.py",
    )

    extract_bls = BashOperator(
        task_id="extract_bls_data",
        cwd=str(REPO_ROOT),
        bash_command=f"{PYTHON_BIN} src/extract/extract_BLS_data.py",
    )

    extract_serp = BashOperator(
        task_id="extract_serp_data",
        cwd=str(REPO_ROOT),
        bash_command=f"{PYTHON_BIN} src/extract/extract_SERP_data.py",
    )

    run_sql_pipeline = BashOperator(
        task_id="run_sql_pipeline",
        cwd=str(REPO_ROOT),
        bash_command=f"{PYTHON_BIN} scripts/run_local_pipeline",
    )

    sync_data_folder = BashOperator(
        task_id="overwrite_repo_data_from_local",
        cwd=str(REPO_ROOT),
        bash_command=f"""
set -euo pipefail
if [ ! -d "{LOCAL_DATA_SOURCE}" ]; then
  echo "LOCAL_DATA_SOURCE does not exist: {LOCAL_DATA_SOURCE}"
  exit 1
fi
mkdir -p "{REPO_DATA_DIR}"
rsync -a --delete "{LOCAL_DATA_SOURCE}/" "{REPO_DATA_DIR}/"
echo "Synced local data into repo data directory."
""",
    )

    push_data_to_github = BashOperator(
        task_id="commit_and_push_data_changes",
        cwd=str(REPO_ROOT),
        bash_command=f"""
set -euo pipefail
export GIT_SSH_COMMAND='ssh -i "{GIT_SSH_KEY_PATH}" -o IdentitiesOnly=yes'
git add data

if git diff --cached --quiet; then
  echo "No data changes to commit."
  exit 0
fi

git commit -m "chore(data): biweekly refresh from local pipeline run"
git push origin main
""",
    )

    extract_fred >> extract_bls >> extract_serp >> run_sql_pipeline >> sync_data_folder >> push_data_to_github
