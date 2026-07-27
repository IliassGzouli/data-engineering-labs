import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_data(df: pd.DataFrame) -> None:
    logger.info("Starting validating data...")

    if df.empty:
        raise ValueError("The transformed dataset is empty.")
    
    required_columns = [
        "status",
        "price",
        "city",
        "state",
        "zip_code",
        "house_size",
        "price_per_sqft"
        ]
    
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )
    
    null_columns = [
        column
        for column in required_columns
        if df[column].isnull().any()
    ]

    if null_columns:
        raise ValueError(
            f"Null values found in required columns: {null_columns}"
        )

    logger.info("Data validation completed successfully.")

    critical_columns = [
        "price",
        "house_size",
        "price_per_sqft"
    ]

    if df[critical_columns].isnull().any().any():
        raise ValueError(
            "Missing values detected in critical columns."
        )
    
    if (df["price"] < 0).any():
        raise ValueError("Negative values found in 'price' column.")
    if (df["house_size"] < 0).any():
        raise ValueError("Negative values found in 'house_size' column.")
    if (df["price_per_sqft"] < 0).any():
        raise ValueError("Negative values found in 'price_per_sqft' column.")
    
    logger.info("Data validation completed successfully.")