import logging

import pyarrow as pa
import pyarrow.compute as pc

logger = logging.getLogger(__name__)


def split_valid_and_quarantine(
    table: pa.Table,
) -> tuple[pa.Table, pa.Table]:
    """
    Split processed NYC Taxi data into valid rows
    and quarantined anomaly rows.

    Adds a quarantine_reason column to quarantined rows.
    """

    invalid_duration = pc.fill_null(
        pc.less_equal(
            table["trip_duration_minutes"],
            0,
        ),
        False,
    )

    negative_distance = pc.fill_null(
        pc.less(
            table["trip_distance"],
            0,
        ),
        False,
    )

    excessive_speed = pc.fill_null(
        pc.greater(
            table["avg_speed_mph"],
            100,
        ),
        False,
    )

    quarantine_mask = pc.or_(
        pc.or_(
            invalid_duration,
            negative_distance,
        ),
        excessive_speed,
    )

    valid_mask = pc.invert(
        quarantine_mask
    )

    valid_table = table.filter(
        valid_mask
    )

    quarantine_table = table.filter(
        quarantine_mask
    )

    quarantine_reasons = pc.if_else(
        invalid_duration,
        "INVALID_DURATION",
        pc.if_else(
            negative_distance,
            "NEGATIVE_DISTANCE",
            pc.if_else(
                excessive_speed,
                "EXCESSIVE_SPEED",
                None,
            ),
        ),
    )

    quarantine_reasons = quarantine_reasons.filter(
        quarantine_mask
    )

    quarantine_table = quarantine_table.append_column(
        "quarantine_reason",
        quarantine_reasons,
    )

    logger.info(
        "Quality split completed: %s valid rows, %s quarantined rows",
        f"{valid_table.num_rows:,}",
        f"{quarantine_table.num_rows:,}",
    )

    return valid_table, quarantine_table