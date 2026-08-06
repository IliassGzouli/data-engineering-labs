import polars as pl

from ingestion.load import load_to_bronze

def test_load_to_bronze_creates_parquet_file(tmp_path):
    # Arrange
    dataframe = pl.DataFrame(
        {
            "order_id": ["order_001", "order_002"],
            "order_status": ["delivered", "shipped"],
        }
    )

    source_file_path = tmp_path / "olist_orders_dataset.csv"
    bronze_data_dir = tmp_path / "bronze"

    # Act
    output_file_path = load_to_bronze(
        dataframe=dataframe,
        source_file_path=source_file_path,
        bronze_data_dir=bronze_data_dir,
    )

    # Assert
    assert output_file_path.exists()
    assert output_file_path.name == "olist_orders_dataset.parquet"


def test_load_to_bronze_writes_expected_content(tmp_path):
    #arrange 
    expected_dataframe = pl.DataFrame(
        {
            "order_id": ["order_001", "order_002"],
            "order_status": ["delivered", "shipped"],
        }
    )

    source_file_path = tmp_path / "olist_orders_dataset.csv"
    bronze_data_dir = tmp_path / "bronze"

    #act
    output_file_path = load_to_bronze(
        dataframe=expected_dataframe,
        source_file_path=source_file_path,
        bronze_data_dir=bronze_data_dir,
    )

    actual_dataframe = pl.read_parquet(output_file_path)

    #assert
    assert actual_dataframe.equals(expected_dataframe)