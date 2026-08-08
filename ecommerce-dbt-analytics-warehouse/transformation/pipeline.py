from pathlib import Path
import polars as pl

from transformation.silver import transform_customers
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