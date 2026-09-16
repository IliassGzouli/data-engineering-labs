import logging
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = Path("data/processed")


def save_processed_parquet(
    table: pa.Table,
    filename: str,
    processed_data_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """
    Save a transformed PyArrow Table as a processed Parquet file.
    """

    processed_data_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = processed_data_dir / filename

    logger.info(
        "Saving processed Parquet file: %s",
        output_path,
    )

    try:
        pq.write_table(
            table,
            output_path,
            compression="snappy",
        )

    except (OSError, pa.ArrowException) as exc:
        logger.error(
            "Failed to save processed Parquet file %s: %s",
            output_path,
            exc,
        )
        raise

    logger.info(
        "Processed Parquet saved successfully: %s rows, %s columns",
        f"{table.num_rows:,}",
        table.num_columns,
    )

    return output_path



