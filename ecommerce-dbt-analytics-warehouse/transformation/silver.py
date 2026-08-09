import polars as pl

def transform_customers(dataframe: pl.DataFrame) -> pl.DataFrame:
    """
    Clean and standardize the customers dataset for the Silver layer.
    """
    return dataframe.with_columns(
        pl.col("customer_zip_code_prefix").cast(pl.String).str.pad_start(5, "0")   
    )  


def transform_orders(dataframe: pl.DataFrame) -> pl.DataFrame:
    """
    Clean and enrich the orders dataset for the Silver layer.
    """
    return dataframe.with_columns(
        (
            (pl.col("order_status") == "delivered")
            & (
                pl.col("order_approved_at").is_null()
                | pl.col("order_delivered_carrier_date").is_null()
                | pl.col("order_delivered_customer_date").is_null()
            )
        ).alias("has_delivery_date_anomaly")
    )


def transform_order_items(dataframe: pl.DataFrame) -> pl.DataFrame:
    """
    Enrich the order items dataset for the Silver layer.
    """
    return dataframe.with_columns(
        (pl.col("price") + pl.col("freight_value")).alias("item_total_value")
    )


def transform_order_payments(dataframe: pl.DataFrame) -> pl.DataFrame:
    """
    Flag suspicious payment records for the Silver layer.
    """
    return dataframe.with_columns(
        (pl.col("payment_value") <= 0).alias("has_invalid_payment_value"),
        (pl.col("payment_type") == "not_defined").alias("has_undefined_payment_type"),
    )

