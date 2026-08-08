import polars as pl

def transform_customers(dataframe: pl.DataFrame) -> pl.DataFrame:
    """
    Clean and standardize the customers dataset for the Silver layer.
    """
    return dataframe.with_columns(
        pl.col("customer_zip_code_prefix").cast(pl.String).str.pad_start(5, "0")   
    )  
