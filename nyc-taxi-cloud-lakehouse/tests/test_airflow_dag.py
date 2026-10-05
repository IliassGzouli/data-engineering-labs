"""Exercise DAG task logic with simulated Airflow interfaces, without a scheduler."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import runpy
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest


class RetryError(Exception):
    pass


class SkipError(Exception):
    pass


@pytest.fixture
def dag_task(monkeypatch):
    context = {
        "dag_run": SimpleNamespace(conf={}),
        "logical_date": datetime(2026, 1, 5, tzinfo=timezone.utc),
        "ti": SimpleNamespace(try_number=1),
    }
    captured = {}
    sdk = ModuleType("airflow.sdk")
    exceptions = ModuleType("airflow.exceptions")

    def dag(**options):
        captured["dag_options"] = options
        return lambda function: function

    def task(**options):
        captured["task_options"] = options

        def decorate(function):
            captured["run"] = function
            # Creating the DAG must not execute the subprocess.
            return lambda: None

        return decorate

    sdk.dag = dag
    sdk.task = task
    sdk.get_current_context = lambda: context
    exceptions.AirflowException = RetryError
    exceptions.AirflowSkipException = SkipError
    monkeypatch.setitem(sys.modules, "airflow", ModuleType("airflow"))
    monkeypatch.setitem(sys.modules, "airflow.sdk", sdk)
    monkeypatch.setitem(sys.modules, "airflow.exceptions", exceptions)
    process = MagicMock()
    monkeypatch.setattr(subprocess, "run", process)
    namespace = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "dags/nyc_taxi_monthly.py")
    )
    return context, captured, process, namespace


def test_dag_schedule_and_retry_settings(dag_task):
    _, captured, process, _ = dag_task
    assert captured["dag_options"]["schedule"] == "0 6 5 * *"
    assert captured["dag_options"]["catchup"] is False
    assert captured["task_options"] == {
        "retries": 3, "retry_delay": timedelta(hours=6)
    }
    process.assert_not_called()


@pytest.mark.parametrize(
    "conf, expected",
    [({}, (2025, 11)), ({"year": "2026", "month": "8"}, (2026, 8)),
     ({"year": 2026}, (2025, 11)), ({"month": 8}, (2025, 11))],
)
def test_dag_target_month(dag_task, conf, expected):
    context, captured, process, namespace = dag_task
    context["dag_run"].conf = conf
    captured["run"]()
    year, month = expected
    process.assert_called_once_with(
        [namespace["PROJECT_PYTHON"], "-m", "orchestration.monthly",
         "--year", str(year), "--month", str(month)],
        cwd=namespace["PROJECT_ROOT"], check=True,
    )


@pytest.mark.parametrize("attempt", [1, 2, 3, 4])
def test_source_unavailable_retries_then_skips(dag_task, attempt):
    context, captured, process, _ = dag_task
    context["ti"].try_number = attempt
    process.side_effect = subprocess.CalledProcessError(75, "pipeline")
    with pytest.raises(RetryError if attempt <= 3 else SkipError):
        captured["run"]()


def test_other_exit_code_remains_failure(dag_task):
    context, captured, process, _ = dag_task
    context["ti"].try_number = 4
    error = subprocess.CalledProcessError(1, "pipeline")
    process.side_effect = error
    with pytest.raises(subprocess.CalledProcessError) as caught:
        captured["run"]()
    assert caught.value is error


def test_invalid_manual_value_does_not_launch_pipeline(dag_task):
    context, captured, process, _ = dag_task
    context["dag_run"].conf = {"year": "invalid", "month": 8}
    with pytest.raises(ValueError):
        captured["run"]()
    process.assert_not_called()
