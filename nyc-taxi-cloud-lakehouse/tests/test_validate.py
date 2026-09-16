from datetime import datetime
import logging

import pyarrow as pa
import pytest

from ingestion.validate import validate_table


def test_validate_table_accepts_valid_data() -> None:
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

    validate_table(table)

def test_validate_table_rejects_empty_table() -> None:
    table = pa.table({})

    with pytest.raises(
        ValueError,
        match="Table is empty",
    ):
        validate_table(table)

def test_validate_table_rejects_missing_required_columns() -> None:
    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 30, 0),
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        validate_table(table)

def test_validate_table_rejects_null_pickup_datetime() -> None:
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

    with pytest.raises(
        ValueError,
        match="tpep_pickup_datetime contains 1 null values",
    ):
        validate_table(table)

def test_validate_table_rejects_null_dropoff_datetime() -> None:
    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                None,
            ],
            "trip_distance": [10.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="tpep_dropoff_datetime contains 1 null values",
    ):
        validate_table(table)

def test_validate_table_warns_for_non_positive_duration(
    caplog: pytest.LogCaptureFixture,
) -> None:
    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
            ],
            "trip_distance": [10.0],
        }
    )

    with caplog.at_level(logging.WARNING):
        validate_table(table)

    assert "duration <= 0" in caplog.text


def test_validate_table_warns_for_negative_distance(
    caplog: pytest.LogCaptureFixture,
) -> None:
    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 30, 0),
            ],
            "trip_distance": [-5.0],
        }
    )

    with caplog.at_level(logging.WARNING):
        validate_table(table)

    assert "negative trip_distance" in caplog.text


def test_validate_table_warns_for_speed_above_100_mph(
    caplog: pytest.LogCaptureFixture,
) -> None:
    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 30, 0),
            ],
            "trip_distance": [60.0],
        }
    )

    with caplog.at_level(logging.WARNING):
        validate_table(table)

    assert "avg_speed > 100 mph" in caplog.text