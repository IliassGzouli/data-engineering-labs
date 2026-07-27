import pandas as pd
from config import PROCESSED_DATA_PATH, SAMPLE_SIZE, RAW_DATA_PATH
from etl.extract import extract
import logging

logger = logging.getLogger(__name__)

def transform(df):
    logger.info("Starting data transformation...")

    df = df.copy()

    logger.info("Shape before transformation: %s", df.shape)

    logger.info("Missing values before transformation:")
    logger.info(df.isnull().sum())

    columns_to_keep = [
        "status",
        "price",
        "bed",
        "bath",
        "acre_lot",
        "city",
        "state",
        "zip_code",
        "house_size",
        "prev_sold_date",
    ] 

    df = df[columns_to_keep]
    df = df.dropna(subset=["price", "house_size"])
    df = df.dropna(subset=["city", "zip_code"])

    df = df[df["price"] > 0]
    df = df[df["house_size"] > 0]

    df["price_per_sqft"] = df["price"] / df["house_size"]

    df["city"] = df["city"].str.lower().str.strip()
    df["state"] = df["state"].str.lower().str.strip()
    df["status"] = df["status"].str.lower().str.strip()

    logger.info("Shape after transformation: %s", df.shape)

    logger.info("Missing values after transformation:")
    logger.info(df.isnull().sum())

    logger.info("Columns after transformation:")
    logger.info(df.columns)
    return df


if __name__ == "__main__":
    df_raw = extract(RAW_DATA_PATH, nrows=SAMPLE_SIZE)
    df_clean = transform(df_raw)

    df_clean.to_csv(PROCESSED_DATA_PATH, index=False)

    logger.info("Transformed data saved successfully.")
    logger.info("Saved file: %s", PROCESSED_DATA_PATH)

    logger.info("First few rows of transformed data:")
    logger.info(df_clean.head())
    logger.info("Shape of transformed data: %s", df_clean.shape)

