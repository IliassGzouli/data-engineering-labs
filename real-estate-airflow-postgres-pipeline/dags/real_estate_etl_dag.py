from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.pipeline import run_pipeline

default_args = {
    "owner": "iliass",
    "retries": 1,
    "retry_delay" : timedelta(minutes=5),
}

with DAG(
    dag_id="real_estate_etl_dag",
    default_args=default_args,
    description="ETL pipeline for real estate data using PostgreSQL",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["real_estate", "ETL", "PostgreSQL"],
) as dag:
    
    run_etl_task = PythonOperator(
        task_id="run_extract_transform_load",
        python_callable=run_pipeline,
    )

run_etl_task
