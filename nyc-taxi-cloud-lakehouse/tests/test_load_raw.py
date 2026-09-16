from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from ingestion.load_raw import load_raw_parquet


def test_load_raw_parquet_loads_valid_file(
    tmp_path: Path,
) -> None:
    table = pa.table(
        {
            "trip_distance": [10.0, 20.0],
        }
    )

    parquet_path = tmp_path / "test.parquet"

    pq.write_table(
        table,
        parquet_path,
    )

    result = load_raw_parquet(parquet_path)

    assert result.num_rows == 2

def test_load_raw_parquet_preserves_columns(
    tmp_path: Path,
) -> None:
    table = pa.table(
        {
            "trip_distance": [10.0],
            "fare_amount": [25.0],
        }
    )

    parquet_path = tmp_path / "test.parquet"

    pq.write_table(
        table,
        parquet_path,
    )

    result = load_raw_parquet(parquet_path)

    assert result.column_names == table.column_names

def test_load_raw_parquet_preserves_values(
    tmp_path: Path,
) -> None:
    table = pa.table(
        {
            "trip_distance": [10.0, 20.0],
        }
    )

    parquet_path = tmp_path / "test.parquet"

    pq.write_table(
        table,
        parquet_path,
    )

    result = load_raw_parquet(parquet_path)

    assert result["trip_distance"].to_pylist() == [10.0, 20.0]

def test_load_raw_parquet_rejects_missing_file(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing.parquet"

    with pytest.raises(
        FileNotFoundError,
        match="Raw Parquet file not found",
    ):
        load_raw_parquet(missing_path)

def test_load_raw_parquet_rejects_directory(
    tmp_path: Path,
) -> None:
    directory_path = tmp_path / "raw"

    directory_path.mkdir()

    with pytest.raises(
        ValueError,
        match="Path is not a file",
    ):
        load_raw_parquet(directory_path)

    