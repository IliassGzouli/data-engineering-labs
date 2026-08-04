import logging
from pathlib import Path
import polars as pl

logger = logging.getLogger(__name__)

def extract_csv(file_path: str | Path) -> pl.DataFrame:
    """
    Read a CSV file and return its content as a Polars DataFrame.

    Args:
        file_path: Path to the CSV file.

    Returns:
        A Polars DataFrame containing the extracted data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the path is invalid or the CSV contains no rows.
        RuntimeError: If Polars cannot read the CSV file.
    """

    path = Path(file_path)
    logger.info("Starting extraction from %s", path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Expected a file but received : {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Unsupported file format: {path.suffix}")

    try:
        dataframe = pl.read_csv(
            path,
            try_parse_dates=True,
            raise_if_empty=True,
        )
    except pl.exceptions.NoDataError as error:
        raise ValueError(f"CSV file is empty: {path}") from error

    except pl.exceptions.PolarsError as error:
        raise RuntimeError(f"Failed to read CSV file: {path}") from error


    if dataframe.height == 0:
        raise ValueError(f"CSV file contains no data rows: {path}")

    logger.info(
        "Extraction completed: file=%s, roxs=%d, columns=%d",
        path.name,
        dataframe.height,
        dataframe.width,
    )
    return dataframe