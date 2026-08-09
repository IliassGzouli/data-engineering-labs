from pathlib import Path
import polars as pl

from transformation.silver import (
    transform_customers,
    transform_orders,
    transform_order_items,
    transform_order_payments,
    transform_products,
    transform_sellers,
    transform_order_reviews)
from transformation.load import load_to_silver

def run_customers_silver_pipeline(
        bronze_file_path: str | Path,
        silver_data_dir: str | Path,
)-> Path:
    """
    Read the Bronze customers dataset, transform it, and load it into Silver.
    """

    bronze_file_path=Path(bronze_file_path)
    silver_data_dir=Path(silver_data_dir)

    dataframe= pl.read_parquet(bronze_file_path)

    transformed_dataframe = transform_customers(dataframe)
    return load_to_silver(
        dataframe=transformed_dataframe,
        source_file_path=bronze_file_path,
        silver_data_dir=silver_data_dir,
    )

def run_orders_silver_pipeline(
    bronze_file_path: str | Path,
    silver_data_dir: str | Path,    
)->Path:
    """
    Read the Bronze orders dataset, transform it, and load it into Silver.
    """
    bronze_file_path = Path(bronze_file_path)
    silver_data_dir = Path(silver_data_dir)

    dataframe = pl.read_parquet(bronze_file_path)

    transformed_dataframe = transform_orders(dataframe)

    return load_to_silver(
        dataframe=transformed_dataframe,
        source_file_path=bronze_file_path,
        silver_data_dir=silver_data_dir,
    )


def run_order_items_silver_pipeline(
    bronze_file_path: str | Path,
    silver_data_dir: str | Path,
) -> Path:
    """
    Read the Bronze order items dataset, transform it, and load it into Silver.
    """
    bronze_file_path = Path(bronze_file_path)
    silver_data_dir = Path(silver_data_dir)

    dataframe = pl.read_parquet(bronze_file_path)

    transformed_dataframe = transform_order_items(dataframe)

    return load_to_silver(
        dataframe=transformed_dataframe,
        source_file_path=bronze_file_path,
        silver_data_dir=silver_data_dir,
    )

def run_order_payments_silver_pipeline(
    bronze_file_path: str | Path,
    silver_data_dir: str | Path,
) -> Path:
    """
    Read the Bronze order payments dataset, transform it, and load it into Silver.
    """
    bronze_file_path = Path(bronze_file_path)
    silver_data_dir = Path(silver_data_dir)

    dataframe = pl.read_parquet(bronze_file_path)

    transformed_dataframe = transform_order_payments(dataframe)

    return load_to_silver(
        dataframe=transformed_dataframe,
        source_file_path=bronze_file_path,
        silver_data_dir=silver_data_dir,
    )

def run_products_silver_pipeline(
    bronze_file_path: str | Path,
    silver_data_dir: str | Path,
) -> Path:
    """
    Read the Bronze products dataset, transform it, and load it into Silver.
    """
    bronze_file_path = Path(bronze_file_path)
    silver_data_dir = Path(silver_data_dir)

    dataframe = pl.read_parquet(bronze_file_path)

    transformed_dataframe = transform_products(dataframe)

    return load_to_silver(
        dataframe=transformed_dataframe,
        source_file_path=bronze_file_path,
        silver_data_dir=silver_data_dir,
    )

def run_sellers_silver_pipeline(
    bronze_file_path: str | Path,
    silver_data_dir: str | Path,
) -> Path:
    """
    Read the Bronze sellers dataset, transform it, and load it into Silver.
    """
    bronze_file_path = Path(bronze_file_path)
    silver_data_dir = Path(silver_data_dir)

    dataframe = pl.read_parquet(bronze_file_path)

    transformed_dataframe = transform_sellers(dataframe)

    return load_to_silver(
        dataframe=transformed_dataframe,
        source_file_path=bronze_file_path,
        silver_data_dir=silver_data_dir,
    )

def run_order_reviews_silver_pipeline(
    bronze_file_path: str | Path,
    silver_data_dir: str | Path,
) -> Path:
    """
    Read the Bronze order reviews dataset, transform it, and load it into Silver.
    """
    bronze_file_path = Path(bronze_file_path)
    silver_data_dir = Path(silver_data_dir)

    dataframe = pl.read_parquet(bronze_file_path)

    transformed_dataframe = transform_order_reviews(dataframe)

    return load_to_silver(
        dataframe=transformed_dataframe,
        source_file_path=bronze_file_path,
        silver_data_dir=silver_data_dir,
    )

