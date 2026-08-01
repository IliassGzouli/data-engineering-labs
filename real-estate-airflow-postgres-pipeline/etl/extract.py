import pandas as pd
from config import RAW_DATA_PATH, SAMPLE_SIZE
import logging

logger = logging.getLogger(__name__)

def extract(file_path, nrows=None):
    logger.info("Starting data extraction...")

    df = pd.read_csv(file_path, nrows=nrows)

    logger.info("Extraction completed successfully.")
    logger.info(f"Dataset shape: {df.shape}")

    return df

if __name__ == "__main__":
    df = extract(RAW_DATA_PATH, nrows=SAMPLE_SIZE)
    logger.info("First few rows of extracted data:")
    logger.info(df.head())
