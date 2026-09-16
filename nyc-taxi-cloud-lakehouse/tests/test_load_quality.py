from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from transformation.load_quality import save_quality_outputs


def test_save_quality_outputs_creates_both_files(
    tmp_path: Path,
) -> None:
    valid_dir = tmp_path / "valid"
    quarantine_dir = tmp_path / "quarantine"

    valid_table = pa.table(
        {
            "trip_distance": [10.0],
        }
    )

    quarantine_table = pa.table(
        {
            "trip_distance": [-5.0],
            "quarantine_reason": ["NEGATIVE_DISTANCE"],
        }
    )

    valid_path, quarantine_path = save_quality_outputs(
        valid_table,
        quarantine_table,
        "test.parquet",
        valid_data_dir=valid_dir,
        quarantine_data_dir=quarantine_dir,
    )

    assert valid_path.exists()
    assert quarantine_path.exists()

def test_save_quality_outputs_returns_expected_paths(
    tmp_path: Path,
) -> None:
    valid_dir = tmp_path / "valid"
    quarantine_dir = tmp_path / "quarantine"

    valid_table = pa.table(
        {
            "trip_distance": [10.0],
        }
    )

    quarantine_table = pa.table(
        {
            "trip_distance": [-5.0],
            "quarantine_reason": ["NEGATIVE_DISTANCE"],
        }
    )

    valid_path, quarantine_path = save_quality_outputs(
        valid_table,
        quarantine_table,
        "test.parquet",
        valid_data_dir=valid_dir,
        quarantine_data_dir=quarantine_dir,
    )

    assert valid_path == valid_dir / "test.parquet"
    assert quarantine_path == quarantine_dir / "test.parquet"

def test_save_quality_outputs_preserves_row_counts(
    tmp_path: Path,
) -> None:
    valid_dir = tmp_path / "valid"
    quarantine_dir = tmp_path / "quarantine"

    valid_table = pa.table(
        {
            "trip_distance": [10.0, 20.0, 30.0],
        }
    )

    quarantine_table = pa.table(
        {
            "trip_distance": [-5.0, 100.0],
            "quarantine_reason": [
                "NEGATIVE_DISTANCE",
                "EXCESSIVE_SPEED",
            ],
        }
    )

    valid_path, quarantine_path = save_quality_outputs(
        valid_table,
        quarantine_table,
        "test.parquet",
        valid_data_dir=valid_dir,
        quarantine_data_dir=quarantine_dir,
    )

    saved_valid = pq.read_table(valid_path)
    saved_quarantine = pq.read_table(quarantine_path)

    assert saved_valid.num_rows == 3
    assert saved_quarantine.num_rows == 2

def test_save_quality_outputs_preserves_quarantine_reason(
    tmp_path: Path,
) -> None:
    valid_dir = tmp_path / "valid"
    quarantine_dir = tmp_path / "quarantine"

    valid_table = pa.table(
        {
            "trip_distance": [10.0],
        }
    )

    quarantine_table = pa.table(
        {
            "trip_distance": [-5.0],
            "quarantine_reason": ["NEGATIVE_DISTANCE"],
        }
    )

    _, quarantine_path = save_quality_outputs(
        valid_table,
        quarantine_table,
        "test.parquet",
        valid_data_dir=valid_dir,
        quarantine_data_dir=quarantine_dir,
    )

    saved_quarantine = pq.read_table(quarantine_path)

    assert (
        saved_quarantine["quarantine_reason"][0].as_py()
        == "NEGATIVE_DISTANCE"
    )

def test_save_quality_outputs_creates_directories(
    tmp_path: Path,
) -> None:
    valid_dir = tmp_path / "valid"
    quarantine_dir = tmp_path / "quarantine"

    valid_table = pa.table(
        {
            "trip_distance": [10.0],
        }
    )

    quarantine_table = pa.table(
        {
            "trip_distance": [-5.0],
            "quarantine_reason": ["NEGATIVE_DISTANCE"],
        }
    )

    save_quality_outputs(
        valid_table,
        quarantine_table,
        "test.parquet",
        valid_data_dir=valid_dir,
        quarantine_data_dir=quarantine_dir,
    )

    assert valid_dir.exists()
    assert quarantine_dir.exists()