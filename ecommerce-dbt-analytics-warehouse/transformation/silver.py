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

def transform_products(dataframe: pl.DataFrame) -> pl.DataFrame:
    """
    Flag incomplete or invalid product records for the Silver layer.
    """
    return dataframe.with_columns(
        pl.any_horizontal(
            pl.col("product_category_name").is_null(),
            pl.col("product_name_lenght").is_null(),
            pl.col("product_description_lenght").is_null(),
            pl.col("product_photos_qty").is_null(),
        ).alias("has_missing_product_metadata"),

        pl.any_horizontal(
            pl.col("product_weight_g").is_null(),
            pl.col("product_length_cm").is_null(),
            pl.col("product_height_cm").is_null(),
            pl.col("product_width_cm").is_null(),
            pl.col("product_weight_g") <= 0,
        ).alias("has_invalid_product_dimensions"),
    ) 

def transform_sellers(dataframe: pl.DataFrame) -> pl.DataFrame:
    """
    Standardize seller ZIP code prefixes for the Silver layer.
    """
    return dataframe.with_columns(
        pl.col("seller_zip_code_prefix").cast(pl.String).str.pad_start(5, "0")   
    )  

def transform_order_reviews(dataframe: pl.DataFrame) -> pl.DataFrame:
    """
    Flag duplicated review IDs for the Silver layer.
    """
    return dataframe.with_columns(
        pl.col("review_id")
        .is_duplicated()
        .alias("has_duplicate_review_id")
    )

def transform_product_category_translation(
    dataframe: pl.DataFrame,
) -> pl.DataFrame:
    """
    Keep the clean product category translation dataset unchanged for Silver.
    """
    return dataframe

def transform_geolocation(dataframe: pl.DataFrame) -> pl.DataFrame:
    """
    Standardize ZIP codes and remove exact duplicate geolocation rows.
    """
    return (
        dataframe
        .with_columns(
            pl.col("geolocation_zip_code_prefix")
            .cast(pl.String)
            .str.pad_start(5, "0")
        )
        .unique()
    )