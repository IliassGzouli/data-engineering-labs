from __future__ import annotations

import logging

import pyarrow as pa
import pyarrow.compute as pc

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "trip_distance",
}


def validate_table(table: pa.Table) -> None:
    """
    Validate core NYC Taxi data quality rules.

    Raises:
        ValueError: If a blocking validation rule fails.
    """

#1-table vide
    if table.num_rows == 0:
        raise ValueError("Table is empty")

#2- colonnes obligatoires
    missing_columns = REQUIRED_COLUMNS - set(table.column_names)

    if missing_columns:
        raise ValueError(
            f"Missing required columns : {sorted(missing_columns)}"
        )

#3 - timestamp NULL
    pickup_nulls = table["tpep_pickup_datetime"].null_count
    dropoff_nulls = table["tpep_dropoff_datetime"].null_count

    if pickup_nulls > 0:
        raise ValueError(
            f"tpep_pickup_datetime contains {pickup_nulls:,} null values"
        )
    if dropoff_nulls > 0:
        raise ValueError(
            f"tpep_dropoff_datetime contains {dropoff_nulls:,} null values"
        )

#4- calcul durée
    duration = pc.subtract(
        table["tpep_dropoff_datetime"], 
        table["tpep_pickup_datetime"],
    )

    duration_us = pc.cast(
        duration,
        pa.int64(),
    )

    duration_seconds = pc.divide(
        pc.cast(duration_us, pa.float64()),
        1_000_000.0,
    )

#5- durée <= 0

    invalid_duration_mask = pc.less_equal(
        duration_seconds,
        0,
    )

    invalid_duration_count = pc.sum(
        pc.cast(
            pc.fill_null(invalid_duration_mask, False),
            pa.int64(),
        )
    ).as_py()

    if invalid_duration_count > 0:
        logger.warning(
            "Found %s rows with duration <= 0",
            f"{invalid_duration_count:,}",
        )

#6 - distance negative

    negative_distance_mask = pc.less(
        table["trip_distance"],
        0,
    )

    negative_distance_count = pc.sum(
        pc.cast(
            pc.fill_null(negative_distance_mask, False),
            pa.int64(),
        )
    ).as_py()

    if negative_distance_count > 0:
        logger.warning(
            "Found %s rows with negative trip_distance",
            f"{negative_distance_count}"
        )

# 7 - vitesse moyenne
    valid_duration_mask = pc.greater(
        duration_seconds,
        0,
    )

    duration_hours = pc.divide(
        duration_seconds,
        3600.0,
    )

    safe_duration_hours = pc.if_else(
        valid_duration_mask,
        duration_hours,
        1.0,
    )

    avg_speed_mph = pc.divide(
        pc.cast(table["trip_distance"], pa.float64()),
        safe_duration_hours,
    )

    avg_speed_mph = pc.if_else(
        valid_duration_mask,
        avg_speed_mph,
        pa.scalar(None, type=pa.float64()),
    )

# 8- Vitesse > 100 mph
    speed_anomaly_mask = pc.greater(
        avg_speed_mph,
        100,
    )

    speed_anomaly_count = pc.sum(
        pc.cast(
            pc.fill_null(speed_anomaly_mask, False),
            pa.int64(),
        )
    ).as_py()

    if speed_anomaly_count > 0:
        logger.warning(
            "Found %s rows with avg_speed > 100 mph",
            f"{speed_anomaly_count:,}",
        )

    logger.info(
        "Validation completed for %s rows",
        f"{table.num_rows:,}",
    )