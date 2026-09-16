from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from transformation.load_processed import save_processed_parquet


def test_save_processed_parquet_creates_file(
    tmp_path: Path,
) -> None:
    table = pa.table(
        {
            "trip_distance": [10.0, 20.0],
            "trip_duration_minutes": [30.0, 40.0],
        }
    )

    output_path = save_processed_parquet(
        table,
        "test.parquet",
        processed_data_dir=tmp_path,
    )

    assert output_path.exists()


def test_save_processed_parquet_returns_expected_path(
    tmp_path: Path,
) -> None:
    table = pa.table(
        {
            "trip_distance": [10.0],
        }
    )

    output_path = save_processed_parquet(
        table,
        "test.parquet",
        processed_data_dir=tmp_path,
    )

    assert output_path == tmp_path / "test.parquet"


def test_save_processed_parquet_preserves_row_count(
    tmp_path: Path,
) -> None:
    table = pa.table(
        {
            "trip_distance": [10.0, 20.0, 30.0],
        }
    )

    output_path = save_processed_parquet(
        table,
        "test.parquet",
        processed_data_dir=tmp_path,
    )

    saved_table = pq.read_table(output_path)

    assert saved_table.num_rows == table.num_rows


def test_save_processed_parquet_preserves_columns(
    tmp_path: Path,
) -> None:
    table = pa.table(
        {
            "trip_distance": [10.0],
            "trip_duration_minutes": [30.0],
        }
    )

    output_path = save_processed_parquet(
        table,
        "test.parquet",
        processed_data_dir=tmp_path,
    )

    saved_table = pq.read_table(output_path)

    assert saved_table.column_names == table.column_names


def test_save_processed_parquet_creates_directory(
    tmp_path: Path,
) -> None:
    processed_dir = tmp_path / "processed"

    table = pa.table(
        {
            "trip_distance": [10.0],
        }
    )

    save_processed_parquet(
        table,
        "test.parquet",
        processed_data_dir=processed_dir,
    )

    assert processed_dir.exists()