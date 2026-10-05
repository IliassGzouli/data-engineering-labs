from pathlib import Path
from unittest.mock import MagicMock

import pytest

from orchestration.monthly import run_monthly_pipeline


def test_run_monthly_pipeline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_path = Path(
        "data/raw/yellow_tripdata_2026-02.parquet"
    )

    mock_ingestion = MagicMock(
        return_value=raw_path,
    )

    mock_transformation = MagicMock()

    monkeypatch.setattr(
        "orchestration.monthly.run_ingestion_pipeline",
        mock_ingestion,
    )

    monkeypatch.setattr(
        "orchestration.monthly.run_transformation_pipeline",
        mock_transformation,
    )

    run_monthly_pipeline(
        year=2026,
        month=2,
    )

    mock_ingestion.assert_called_once_with(
        year=2026,
        month=2,
    )

    mock_transformation.assert_called_once_with(
        raw_path
    )

@pytest.mark.parametrize("status", [403, 404])
def test_cli_returns_source_unavailable(monkeypatch, status):
    from requests import Response
    from requests.exceptions import HTTPError
    from orchestration.monthly import main

    response = Response()
    response.status_code = status
    run = MagicMock(side_effect=HTTPError(response=response))
    monkeypatch.setattr("orchestration.monthly.run_monthly_pipeline", run)

    assert main(["--year", "2026", "--month", "8"]) == 75
    run.assert_called_once_with(year=2026, month=8)


@pytest.mark.parametrize("status", [401, 500, None])
def test_cli_propagates_other_http_errors(monkeypatch, status):
    from requests import Response
    from requests.exceptions import HTTPError
    from orchestration.monthly import main

    response = None
    if status is not None:
        response = Response()
        response.status_code = status
    error = HTTPError(response=response)
    monkeypatch.setattr(
        "orchestration.monthly.run_monthly_pipeline",
        MagicMock(side_effect=error),
    )
    with pytest.raises(HTTPError) as caught:
        main(["--year", "2026", "--month", "8"])
    assert caught.value is error


def test_cli_success(monkeypatch):
    from orchestration.monthly import main

    run = MagicMock()
    monkeypatch.setattr("orchestration.monthly.run_monthly_pipeline", run)
    assert main(["--year", "2026", "--month", "8"]) == 0
    run.assert_called_once_with(year=2026, month=8)


@pytest.mark.parametrize("args", [[], ["--year", "invalid", "--month", "8"]])
def test_cli_rejects_invalid_arguments(monkeypatch, args):
    from orchestration.monthly import main

    run = MagicMock()
    monkeypatch.setattr("orchestration.monthly.run_monthly_pipeline", run)
    with pytest.raises(SystemExit) as caught:
        main(args)
    assert caught.value.code == 2
    run.assert_not_called()


@pytest.mark.parametrize("year, month", [(2008, 1), (2026, 0), (2026, 13)])
def test_cli_rejects_invalid_calendar_without_network(year, month):
    from orchestration.monthly import main

    # Ingestion validates the date before any request or AWS operation.
    with pytest.raises(ValueError):
        main(["--year", str(year), "--month", str(month)])
