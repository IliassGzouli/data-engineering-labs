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