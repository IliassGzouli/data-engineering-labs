import logging
from pathlib import Path

import polars as pl 

logger = logging.getLogger(__name__)

def load_to_bronze(
    dataframe: pl.DataFrame,
    source_file_path: str | Path,
    bronze_data_dir: str | Path,
) -> Path:

    """
    Write a validated Polars DataFrame to the Bronze layer
    as a Parquet file.

    Returns:
        Path of the created Parquet file.
    """

    source_file_path = Path(source_file_path)
    bronze_data_dir = Path(bronze_data_dir)

    bronze_data_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file_path = (
        bronze_data_dir / f"{source_file_path.stem}.parquet"
    )

    logger.info("Loading dataset to Bronze: %s", output_file_path)

    dataframe.write_parquet(output_file_path)

    logger.info(
        "Bronze load completed: file=%s, rows=%d, columns=%d",
        output_file_path.name,
        dataframe.height,
        dataframe.width,
    )

    return output_file_path