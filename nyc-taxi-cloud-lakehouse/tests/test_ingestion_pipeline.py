from pathlib import Path
from unittest.mock import MagicMock

import pyarrow as pa
import pytest

from ingestion.pipeline import run_ingestion_pipeline


def test_ingestion_pipeline_downloads_validates_and_uploads(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parquet_path = tmp_path / "yellow_tripdata_2026-01.parquet"

    table = pa.table(
        {
            "tpep_pickup_datetime": [1],
            "tpep_dropoff_datetime": [2],
            "trip_distance": [3.5],
        }
    )

    mock_download = MagicMock(
        return_value=parquet_path,
    )

    mock_load = MagicMock(
        return_value=table,
    )

    mock_validate = MagicMock()

    mock_upload = MagicMock()

    monkeypatch.setattr(
        "ingestion.pipeline.download_yellow_taxi_data",
        mock_download,
    )

    monkeypatch.setattr(
        "ingestion.pipeline.load_raw_parquet",
        mock_load,
    )

    monkeypatch.setattr(
        "ingestion.pipeline.validate_table",
        mock_validate,
    )

    monkeypatch.setattr(
        "ingestion.pipeline.upload_file_to_s3",
        mock_upload,
    )

    run_ingestion_pipeline(
        year=2026,
        month=1,
    )

    mock_download.assert_called_once_with(
        year=2026,
        month=1,
    )

    mock_load.assert_called_once_with(
        parquet_path,
    )

    mock_validate.assert_called_once_with(
        table,
    )

    mock_upload.assert_called_once_with(
    local_path=parquet_path,
    bucket_name="iliass-nyc-taxi-lakehouse-2026",
    object_key="raw/yellow_tripdata_2026-01.parquet",
)