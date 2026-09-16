import pyarrow as pa

from transformation.quarantine import split_valid_and_quarantine


def test_split_keeps_valid_rows() -> None:
    table = pa.table(
        {
            "trip_duration_minutes": [30.0],
            "trip_distance": [10.0],
            "avg_speed_mph": [20.0],
        }
    )

    valid, quarantine = split_valid_and_quarantine(table)

    assert valid.num_rows == 1
    assert quarantine.num_rows == 0

def test_split_quarantines_invalid_duration() -> None:
    table = pa.table(
        {
            "trip_duration_minutes": [0.0],
            "trip_distance": [10.0],
            "avg_speed_mph": [None],
        }
    )

    valid, quarantine = split_valid_and_quarantine(table)

    assert valid.num_rows == 0
    assert quarantine.num_rows == 1
    assert quarantine["quarantine_reason"][0].as_py() == "INVALID_DURATION"

def test_split_quarantines_negative_distance() -> None:
    table = pa.table(
        {
            "trip_duration_minutes": [30.0],
            "trip_distance": [-5.0],
            "avg_speed_mph": [-10.0],
        }
    )

    valid, quarantine = split_valid_and_quarantine(table)

    assert valid.num_rows == 0
    assert quarantine.num_rows == 1
    assert quarantine["quarantine_reason"][0].as_py() == "NEGATIVE_DISTANCE"

def test_split_quarantines_excessive_speed() -> None:
    table = pa.table(
        {
            "trip_duration_minutes": [30.0],
            "trip_distance": [60.0],
            "avg_speed_mph": [120.0],
        }
    )

    valid, quarantine = split_valid_and_quarantine(table)

    assert valid.num_rows == 0
    assert quarantine.num_rows == 1
    assert quarantine["quarantine_reason"][0].as_py() == "EXCESSIVE_SPEED"

def test_split_separates_valid_and_quarantine_rows() -> None:
    table = pa.table(
        {
            "trip_duration_minutes": [
                30.0,
                0.0,
                20.0,
                15.0,
            ],
            "trip_distance": [
                10.0,
                5.0,
                -3.0,
                40.0,
            ],
            "avg_speed_mph": [
                20.0,
                None,
                -9.0,
                160.0,
            ],
        }
    )

    valid, quarantine = split_valid_and_quarantine(table)

    assert valid.num_rows == 1
    assert quarantine.num_rows == 3


def test_quarantine_contains_reason_column() -> None:
    table = pa.table(
        {
            "trip_duration_minutes": [0.0],
            "trip_distance": [5.0],
            "avg_speed_mph": [None],
        }
    )

    _, quarantine = split_valid_and_quarantine(table)

    assert "quarantine_reason" in quarantine.column_names

def test_split_preserves_total_row_count() -> None:
    table = pa.table(
        {
            "trip_duration_minutes": [
                30.0,
                0.0,
                20.0,
            ],
            "trip_distance": [
                10.0,
                5.0,
                -2.0,
            ],
            "avg_speed_mph": [
                20.0,
                None,
                -6.0,
            ],
        }
    )

    valid, quarantine = split_valid_and_quarantine(table)

    assert valid.num_rows + quarantine.num_rows == table.num_rows