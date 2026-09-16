from datetime import datetime

import pyarrow as pa
import pytest

from transformation.transform import transform_trips


def test_transform_trips_adds_derived_columns() -> None:
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

    result = transform_trips(table)

    assert "trip_duration_minutes" in result.column_names
    assert "avg_speed_mph" in result.column_names

def test_transform_trips_calculates_duration() -> None:
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

    result = transform_trips(table)

    duration = result["trip_duration_minutes"][0].as_py()

    assert duration == pytest.approx(30.0)

def test_transform_trips_calculates_average_speed() -> None:
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

    result = transform_trips(table)

    speed = result["avg_speed_mph"][0].as_py()

    assert speed == pytest.approx(30.0)

def test_transform_trips_sets_speed_null_for_zero_duration() -> None:
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

    result = transform_trips(table)

    speed = result["avg_speed_mph"][0].as_py()

    assert speed is None

def test_transform_trips_preserves_row_count() -> None:
    table = pa.table(
        {
            "tpep_pickup_datetime": [
                datetime(2026, 1, 1, 10, 0, 0),
                datetime(2026, 1, 1, 11, 0, 0),
            ],
            "tpep_dropoff_datetime": [
                datetime(2026, 1, 1, 10, 30, 0),
                datetime(2026, 1, 1, 11, 15, 0),
            ],
            "trip_distance": [
                15.0,
                5.0,
            ],
        }
    )

    result = transform_trips(table)

    assert result.num_rows == table.num_rows