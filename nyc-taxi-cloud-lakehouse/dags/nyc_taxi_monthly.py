import subprocess

from airflow.sdk import dag, task, get_current_context
from dateutil.relativedelta import relativedelta


PROJECT_ROOT = "/Users/gzouliiliass/data-engineering-labs/nyc-taxi-cloud-lakehouse"
PROJECT_PYTHON = "/Users/gzouliiliass/environments/data_engineering/bin/python"

SOURCE_LAG_MONTHS = 2


@dag(
    dag_id="nyc_taxi_monthly",
    schedule="0 6 5 * *",
    catchup=False,
    tags=["nyc-taxi", "aws", "monthly"],
)
def nyc_taxi_monthly():

    @task
    def run_target_month() -> None:
        context = get_current_context()

        logical_date = context["logical_date"]

        target_date = logical_date - relativedelta(
            months=SOURCE_LAG_MONTHS,
        )

        subprocess.run(
            [
                PROJECT_PYTHON,
                "-m",
                "orchestration.monthly",
                "--year",
                str(target_date.year),
                "--month",
                str(target_date.month),
            ],
            cwd=PROJECT_ROOT,
            check=True,
        )

    run_target_month()


nyc_taxi_monthly()