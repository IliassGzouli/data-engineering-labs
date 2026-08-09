import polars as pl

from transformation.silver import transform_customers, transform_order_items, transform_order_payments
from transformation.pipeline import run_customers_silver_pipeline
from transformation.pipeline import run_orders_silver_pipeline
from transformation.pipeline import run_order_items_silver_pipeline
from transformation.pipeline import run_order_payments_silver_pipeline

def test_transform_customers_formats_zip_code_prefix():
    dataframe = pl.DataFrame(
        {
            "customer_id": ["c1"],
            "customer_unique_id": ["u1"],
            "customer_zip_code_prefix": [9790],
            "customer_city": ["sao bernardo do campo"],
            "customer_state": ["SP"],
        }
    )

    result = transform_customers(dataframe)

    assert result["customer_zip_code_prefix"][0] == "09790"

def test_transform_customers_keeps_five_digit_zip_code_prefix():
    dataframe = pl.DataFrame(
        {
            "customer_id": ["c1"],
            "customer_unique_id": ["u1"],
            "customer_zip_code_prefix": [14409],
            "customer_city": ["franca"],
            "customer_state": ["SP"],
        }
    )

    result = transform_customers(dataframe)

    assert result["customer_zip_code_prefix"][0] == "14409"

from transformation.load import load_to_silver


def test_load_to_silver_creates_parquet_file(tmp_path):
    dataframe = pl.DataFrame(
        {
            "customer_id": ["c1"],
            "customer_unique_id": ["u1"],
            "customer_zip_code_prefix": ["09790"],
            "customer_city": ["sao bernardo do campo"],
            "customer_state": ["SP"],
        }
    )

    output_file = load_to_silver(
        dataframe=dataframe,
        source_file_path="olist_customers_dataset.parquet",
        silver_data_dir=tmp_path,
    )

    assert output_file.exists()


def test_run_customers_silver_pipeline_creates_transformed_file(tmp_path):
    bronze_file = tmp_path / "olist_customers_dataset.parquet"
    silver_dir = tmp_path / "silver"

    dataframe = pl.DataFrame(
        {
            "customer_id": ["c1"],
            "customer_unique_id": ["u1"],
            "customer_zip_code_prefix": [9790],
            "customer_city": ["sao bernardo do campo"],
            "customer_state": ["SP"],
        }
    )

    dataframe.write_parquet(bronze_file)

    output_file = run_customers_silver_pipeline(
        bronze_file_path=bronze_file,
        silver_data_dir=silver_dir,
    )

    result = pl.read_parquet(output_file)

    assert output_file.exists()
    assert result["customer_zip_code_prefix"][0] == "09790"

from transformation.silver import transform_orders


def test_transform_orders_flags_delivered_order_with_missing_date():
    dataframe = pl.DataFrame(
        {
            "order_id": ["o1"],
            "customer_id": ["c1"],
            "order_status": ["delivered"],
            "order_purchase_timestamp": [None],
            "order_approved_at": [None],
            "order_delivered_carrier_date": [None],
            "order_delivered_customer_date": [None],
            "order_estimated_delivery_date": [None],
        }
    )

    result = transform_orders(dataframe)

    assert result["has_delivery_date_anomaly"][0] is True


def test_transform_orders_does_not_flag_shipped_order_with_missing_customer_date():
    dataframe = pl.DataFrame(
        {
            "order_id": ["o1"],
            "customer_id": ["c1"],
            "order_status": ["shipped"],
            "order_purchase_timestamp": [None],
            "order_approved_at": [None],
            "order_delivered_carrier_date": [None],
            "order_delivered_customer_date": [None],
            "order_estimated_delivery_date": [None],
        }
    )

    result = transform_orders(dataframe)

    assert result["has_delivery_date_anomaly"][0] is False

def test_transform_orders_does_not_flag_complete_delivered_order():
    dataframe = pl.DataFrame(
        {
            "order_id": ["o1"],
            "customer_id": ["c1"],
            "order_status": ["delivered"],
            "order_purchase_timestamp": [None],
            "order_approved_at": ["2018-01-01"],
            "order_delivered_carrier_date": ["2018-01-02"],
            "order_delivered_customer_date": ["2018-01-05"],
            "order_estimated_delivery_date": [None],
        }
    )

    result = transform_orders(dataframe)

    assert result["has_delivery_date_anomaly"][0] is False


def test_run_orders_silver_pipeline_creates_transformed_file(tmp_path):
    bronze_file = tmp_path / "olist_orders_dataset.parquet"
    silver_dir = tmp_path / "silver"

    dataframe = pl.DataFrame(
        {
            "order_id": ["o1"],
            "customer_id": ["c1"],
            "order_status": ["delivered"],
            "order_purchase_timestamp": [None],
            "order_approved_at": [None],
            "order_delivered_carrier_date": [None],
            "order_delivered_customer_date": [None],
            "order_estimated_delivery_date": [None],
        }
    )

    dataframe.write_parquet(bronze_file)

    output_file = run_orders_silver_pipeline(
        bronze_file_path=bronze_file,
        silver_data_dir=silver_dir,
    )

    result = pl.read_parquet(output_file)

    assert output_file.exists()
    assert result["has_delivery_date_anomaly"][0] is True

from transformation.silver import transform_order_items


def test_transform_order_items_calculates_item_total_value():
    # Arrange
    dataframe = pl.DataFrame(
        {
            "order_id": ["o1"],
            "order_item_id": [1],
            "product_id": ["p1"],
            "seller_id": ["s1"],
            "shipping_limit_date": [None],
            "price": [100.0],
            "freight_value": [20.0],
        }
    )

    # Act
    result = transform_order_items(dataframe)

    # Assert
    assert result["item_total_value"][0] == 120.0


def test_run_order_items_silver_pipeline_creates_transformed_file(tmp_path):
    # Arrange
    bronze_file = tmp_path / "olist_order_items_dataset.parquet"
    silver_dir = tmp_path / "silver"

    dataframe = pl.DataFrame(
        {
            "order_id": ["o1"],
            "order_item_id": [1],
            "product_id": ["p1"],
            "seller_id": ["s1"],
            "shipping_limit_date": [None],
            "price": [100.0],
            "freight_value": [20.0],
        }
    )

    dataframe.write_parquet(bronze_file)

    # Act
    output_file = run_order_items_silver_pipeline(
        bronze_file_path=bronze_file,
        silver_data_dir=silver_dir,
    )

    result = pl.read_parquet(output_file)

    # Assert
    assert output_file.exists()
    assert result["item_total_value"][0] == 120.0


def test_transform_order_payments_flags_invalid_payment():
    # Arrange
    dataframe = pl.DataFrame(
        {
            "order_id": ["o1"],
            "payment_sequential": [1],
            "payment_type": ["not_defined"],
            "payment_installments": [1],
            "payment_value": [0.0],
        }
    )

    # Act
    result = transform_order_payments(dataframe)

    # Assert
    assert result["has_invalid_payment_value"][0] is True
    assert result["has_undefined_payment_type"][0] is True


def test_transform_order_payments_does_not_flag_valid_payment():
    # Arrange
    dataframe = pl.DataFrame(
        {
            "order_id": ["o1"],
            "payment_sequential": [1],
            "payment_type": ["credit_card"],
            "payment_installments": [2],
            "payment_value": [100.0],
        }
    )

    # Act
    result = transform_order_payments(dataframe)

    # Assert
    assert result["has_invalid_payment_value"][0] is False
    assert result["has_undefined_payment_type"][0] is False


def test_run_order_payments_silver_pipeline_creates_transformed_file(tmp_path):
    # Arrange
    bronze_file = tmp_path / "olist_order_payments_dataset.parquet"
    silver_dir = tmp_path / "silver"

    dataframe = pl.DataFrame(
        {
            "order_id": ["o1"],
            "payment_sequential": [1],
            "payment_type": ["not_defined"],
            "payment_installments": [1],
            "payment_value": [0.0],
        }
    )

    dataframe.write_parquet(bronze_file)

    # Act
    output_file = run_order_payments_silver_pipeline(
        bronze_file_path=bronze_file,
        silver_data_dir=silver_dir,
    )

    result = pl.read_parquet(output_file)

    # Assert
    assert output_file.exists()
    assert result["has_invalid_payment_value"][0] is True
    assert result["has_undefined_payment_type"][0] is True
