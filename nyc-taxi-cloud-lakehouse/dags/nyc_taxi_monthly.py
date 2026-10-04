import subprocess
from datetime import timedelta

from airflow.sdk import dag, task, get_current_context
from airflow.exceptions import AirflowException, AirflowSkipException
from dateutil.relativedelta import relativedelta


PROJECT_ROOT = "/Users/gzouliiliass/data-engineering-labs/nyc-taxi-cloud-lakehouse"
PROJECT_PYTHON = "/Users/gzouliiliass/environments/data_engineering/bin/python"

SOURCE_LAG_MONTHS = 2
SOURCE_RETRIES = 3
SOURCE_RETRY_DELAY = timedelta(hours=6)
SOURCE_UNAVAILABLE_EXIT_CODE = 75


@dag(
    dag_id="nyc_taxi_monthly",
    schedule="0 6 5 * *",
    catchup=False,
    tags=["nyc-taxi", "aws", "monthly"],
)
def nyc_taxi_monthly():
    @task(
        retries=SOURCE_RETRIES,
        retry_delay=SOURCE_RETRY_DELAY,
    )
    def run_target_month() -> None:
        context = get_current_context()

        dag_run = context["dag_run"]
        logical_date = context["logical_date"]

        conf = dag_run.conf or {}

        if "year" in conf and "month" in conf:
            target_year = int(conf["year"])
            target_month = int(conf["month"])
        else:
            target_date = logical_date - relativedelta(
                months=SOURCE_LAG_MONTHS,
            )
            target_year = target_date.year
            target_month = target_date.month

        try:
            subprocess.run(
                [
                    PROJECT_PYTHON,
                    "-m",
                    "orchestration.monthly",
                    "--year",
                    str(target_year),
                    "--month",
                    str(target_month),
                ],
                cwd=PROJECT_ROOT,
                check=True,
            )

        except subprocess.CalledProcessError as exc:
            if exc.returncode != SOURCE_UNAVAILABLE_EXIT_CODE:
                raise

            task_instance = context["ti"]

            if task_instance.try_number <= SOURCE_RETRIES:
                raise AirflowException(
                    f"NYC Taxi source unavailable for "
                    f"{target_year:04d}-{target_month:02d}. "
                    f"Airflow will retry."
                )

            raise AirflowSkipException(
                f"NYC Taxi source still unavailable for "
                f"{target_year:04d}-{target_month:02d} "
                f"after {SOURCE_RETRIES} retries."
            )

    run_target_month()


nyc_taxi_monthly()