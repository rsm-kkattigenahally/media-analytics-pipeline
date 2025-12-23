import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.transfers.copy_into_snowflake import (
        CopyFromExternalStageToSnowflakeOperator,
    )
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
    "retry_delay": timedelta(seconds=10),
    "snowflake_conn_id": "snowflake_conn"
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
    
    # load_to_snowflake = SnowflakeOperator(
    #     task_id="load_silver_to_snowflake",
    #     snowflake_conn_id="snowflake_conn",
    #     sql="""
    #         COPY INTO spotify_plays
    #         FROM @spotify_stage/spotify_silver_20251221_231437.parquet
    #         MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
    #         FILE_FORMAT = (TYPE=PARQUET)
    #         ON_ERROR = 'CONTINUE';
    #     """,
    #     warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'MEDIA_WH'),
    #     database=os.getenv('SNOWFLAKE_DATABASE', 'MEDIA_ANALYZER'),
    #     schema=os.getenv('SNOWFLAKE_SCHEMA', 'SPOTIFY'),
    #     role=os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN'),
    # )
   

    
    load_to_snowflake = CopyFromExternalStageToSnowflakeOperator(
        task_id="load_silver_to_snowflake",
        table="SPOTIFY_PLAYS",
        stage="SPOTIFY_STAGE",
        files=["spotify_silver_20251222_020057.parquet"],
        file_format="(TYPE = PARQUET)",
        copy_options="MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE",
    )

 
    ingest_task >> transform_task >> load_to_snowflake
    