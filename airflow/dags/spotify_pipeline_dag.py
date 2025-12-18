import sys
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Add ingestion and transform modules to PYTHONPATH
sys.path.append("/opt/airflow/ingestion")
sys.path.append("/opt/airflow/transform")

# Import your scripts
from ingest import main as ingest_main             # ingestion/ingest.py
from clean_spotify import main as transform_main   # transform/clean_spotify.py

default_args = {
    "owner": "komal",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="spotify_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_spotify",
        python_callable=ingest_main,
    )

    transform_task = PythonOperator(
        task_id="transform_spotify",
        python_callable=transform_main,
        op_kwargs={"filename": "{{ ti.xcom_pull(task_ids='ingest_spotify') }}"}
    )

    ingest_task >> transform_task
