from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from transformation.pipeline import run_transformation_pipeline


def test_pipeline_creates_all_outputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_path = tmp_path / "raw.parquet"

    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 30, 0),
            ],
            "trip_distance": [10.0],
        }
    )

    pq.write_table(table, raw_path)

    processed_dir = tmp_path / "processed"
    valid_dir = tmp_path / "valid"
    quarantine_dir = tmp_path / "quarantine"

    monkeypatch.setattr(
        "transformation.load_processed.PROCESSED_DATA_DIR",
        processed_dir,
    )

    monkeypatch.setattr(
        "transformation.load_quality.VALID_DATA_PATH",
        valid_dir,
    )

    monkeypatch.setattr(
        "transformation.load_quality.QUARANTINE_DATA_PATH",
        quarantine_dir,
    )

    processed_path, valid_path, quarantine_path = (
        run_transformation_pipeline(raw_path)
    )

    assert processed_path.exists()
    assert valid_path.exists()
    assert quarantine_path.exists()


def test_pipeline_transforms_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_path = tmp_path / "raw.parquet"

    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 30, 0),
            ],
            "trip_distance": [15.0],
        }
    )

    pq.write_table(table, raw_path)

    processed_dir = tmp_path / "processed"

    monkeypatch.setattr(
        "transformation.load_processed.PROCESSED_DATA_DIR",
        processed_dir,
    )

    processed_path, _, _ = run_transformation_pipeline(raw_path)

    processed_table = pq.read_table(processed_path)

    assert "trip_duration_minutes" in processed_table.column_names
    assert "avg_speed_mph" in processed_table.column_names


def test_pipeline_separates_valid_and_quarantine(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_path = tmp_path / "raw.parquet"

    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
                datetime(2026, 1, 1, 11, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 30, 0),
                datetime(2026, 1, 1, 11, 0, 0),
            ],
            "trip_distance": [
                10.0,
                5.0,
            ],
        }
    )

    pq.write_table(table, raw_path)

    valid_dir = tmp_path / "valid"
    quarantine_dir = tmp_path / "quarantine"

    monkeypatch.setattr(
        "transformation.load_quality.VALID_DATA_PATH",
        valid_dir,
    )

    monkeypatch.setattr(
        "transformation.load_quality.QUARANTINE_DATA_PATH",
        quarantine_dir,
    )

    _, valid_path, quarantine_path = run_transformation_pipeline(raw_path)

    valid_table = pq.read_table(valid_path)
    quarantine_table = pq.read_table(quarantine_path)

    assert valid_table.num_rows == 1
    assert quarantine_table.num_rows == 1


def test_pipeline_stops_on_blocking_validation_error(
    tmp_path: Path,
) -> None:
    raw_path = tmp_path / "raw.parquet"

    table = pa.table(
        {
            "tpep_pickup_datetime": [
                None,
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 30, 0),
            ],
            "trip_distance": [10.0],
        }
    )

    pq.write_table(table, raw_path)

    with pytest.raises(
        ValueError,
        match="tpep_pickup_datetime contains 1 null values",
    ):
        run_transformation_pipeline(raw_path)


def test_pipeline_preserves_total_row_count(
    tmp_path: Path,
) -> None:
    raw_path = tmp_path / "raw.parquet"

    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
                datetime(2026, 1, 1, 11, 0, 0),
                datetime(2026, 1, 1, 12, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 30, 0),
                datetime(2026, 1, 1, 11, 0, 0),
                datetime(2026, 1, 1, 12, 30, 0),
            ],
            "trip_distance": [
                10.0,
                5.0,
                -3.0,
            ],
        }
    )

    pq.write_table(table, raw_path)

    _, valid_path, quarantine_path = run_transformation_pipeline(raw_path)

    valid_table = pq.read_table(valid_path)
    quarantine_table = pq.read_table(quarantine_path)

    assert (
        valid_table.num_rows + quarantine_table.num_rows
        == table.num_rows
    )