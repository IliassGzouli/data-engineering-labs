import polars as pl

from transformation.silver import transform_customers
from transformation.pipeline import run_customers_silver_pipeline


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