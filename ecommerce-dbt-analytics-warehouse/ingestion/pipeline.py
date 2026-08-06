import logging
from pathlib import Path

from ingestion.extract import extract_csv
from ingestion.validate import validate_dataset
from ingestion.load import load_to_bronze

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

def run_ingestion_pipeline(
        raw_data_dir: str | Path,
        bronze_data_dir: str | Path)-> None:
    """
    Extract, validate and load every CSV file into the Bronze layer.
    """

    raw_data_dir=Path(raw_data_dir)
    bronze_data_dir=Path(bronze_data_dir)

    csv_files = sorted(
        raw_data_dir.glob("*.csv")
    )

    if not csv_files:
        raise ValueError(
            f"No CSV files found in the raw data directory: {raw_data_dir}"
        )

    for file_path in csv_files:
        logger.info(
            "Processing file: %s",
            file_path.name,
        )

        dataframe = extract_csv(file_path)

        validate_dataset(
            dataframe=dataframe,
            file_path=file_path,
        )

        logger.info(
            "File validated successfully: %s",
            file_path.name,
        )

        output_file_path = load_to_bronze(
            dataframe=dataframe,
            source_file_path=file_path,
            bronze_data_dir=bronze_data_dir,
        )

        logger.info(
            "File loaded succesfully into Bronze: %s",
            output_file_path,
        )

if __name__ == "__main__":
    run_ingestion_pipeline(
        raw_data_dir="data/raw",
        bronze_data_dir="data/bronze",
        )
