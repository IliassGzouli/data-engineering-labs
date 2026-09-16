import logging 

import pyarrow as pa
import pyarrow.compute as pc

logger = logging.getLogger(__name__)

def transform_trips(table: pa.Table) -> pa.Table:
    """
    Add derived columns to NYC Taxi trips.

    Added columns:
    - trip_duration_minutes
    - avg_speed_mph
    """
    logger.info(
        "Starting transformation for %s rows",
        f"{table.num_rows:,}",
    )

    # 1. Calcul de la durée
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

    duration_minutes = pc.divide(
        duration_seconds,
        60.0,
    ) 

    # 2. Calcul de la vitesse moyenne
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

    # 3. Ajout des colonnes

    transformed_table = table.append_column(
        "trip_duration_minutes",
        duration_minutes,
    )

    transformed_table = transformed_table.append_column(
        "avg_speed_mph",
        avg_speed_mph,
    )

    logger.info(
        "Transformation completed: %s rows, %s columns",
        f"{transformed_table.num_rows:,}",
        transformed_table.num_columns,
    )

    return transformed_table