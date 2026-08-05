import polars as pl
import pytest

from ingestion.validate import validate_dataframe, validate_dataset

def test_validate_dataframe_accepts_valid_data():
    #arrange
    dataframe = pl.DataFrame(
        {
            "order_id": ["order_001", "order_002"],
            "customer_id": ["customer_001", "customer_002"],
            "order_status": ["delivered", "shipped"],
        }
    )

    #act
    result = validate_dataframe(
        dataframe=dataframe,
        required_columns={
            "order_id",
            "customer_id",
            "order_status"
        },
        unique_columns=["order_id"],
        non_null_columns=[
            "order_id",
            "customer_id",
            "order_status"
        ],
    )

    #assert
    assert result is None


def test_validate_dataframe_rejects_empty_dataframe():
    #arrange
    dataframe=pl.DataFrame()

    #act and assert
    with pytest.raises(ValueError, match="DataFrame is empty"):
        validate_dataframe(
            dataframe=dataframe,
            required_columns={"order_id"},
        )

def test_validate_dataframe_detects_missing_required_columns():
    # Arrange
    dataframe = pl.DataFrame(
        {
            "order_id": ["order_001"],
            "customer_id": ["customer_001"],
        }
    )

    required_columns = {
        "order_id",
        "customer_id",
        "order_status",
    }

    # Act and Assert
    with pytest.raises(
        ValueError,
        match="Missing required columns: order_status",
    ):
        validate_dataframe(
            dataframe=dataframe,
            required_columns=required_columns,
        )


def test_validate_dataframe_detects_null_values():
    # Arrange
    dataframe = pl.DataFrame(
        {
            "order_id": ["order_001", "order_002"],
            "customer_id": ["customer_001", None],
        }
    )

    # Act and Assert
    with pytest.raises(
        ValueError,
        match="Column 'customer_id' contains 1 null value",
    ):
        validate_dataframe(
            dataframe=dataframe,
            required_columns={"order_id", "customer_id"},
            non_null_columns=["customer_id"],
        )


def test_validate_dataframe_detects_duplicate_values():
    # Arrange
    dataframe = pl.DataFrame(
        {
            "order_id": ["order_001", "order_001", "order_002"],
            "customer_id": [
                "customer_001",
                "customer_001",
                "customer_002",
            ],
        }
    )

    # Act and Assert
    with pytest.raises(
        ValueError,
        match="Found 1 duplicate row",
    ):
        validate_dataframe(
            dataframe=dataframe,
            required_columns={"order_id", "customer_id"},
            unique_columns=["order_id"],
        )


def test_validate_dataframe_rejects_unknown_validation_column():
    # Arrange
    dataframe = pl.DataFrame(
        {
            "order_id": ["order_001"],
            "customer_id": ["customer_001"],
        }
    )

    # Act and Assert
    with pytest.raises(
        ValueError,
        match="Validation columns not found: orders_id",
    ):
        validate_dataframe(
            dataframe=dataframe,
            required_columns={"order_id", "customer_id"},
            unique_columns=["orders_id"],
        )


def test_validate_dataset_uses_correct_schema():
    #arrange
    dataframe = pl.DataFrame(
        {
            "customer_id": ["customer_001"],
            "customer_unique_id": ["unique_001"],
            "customer_zip_code_prefix": [1000],
            "customer_city": ["sao paulo"],
            "customer_state": ["SP"],
        }
    )

    #act 
    result = validate_dataset(
        dataframe=dataframe,
        file_path="data/raw/olist_customers_dataset.csv",
    )

    #assert
    assert result is None


def test_validate_dataset_rejects_unknown_file():
    #arrange
    dataframe=pl.DataFrame(
        {
            "id": [1],
        }
    )

    #act and assert
    with pytest.raises(ValueError, match="No validation schema found for file: unknown.csv",):
        validate_dataset(
            dataframe=dataframe,
            file_path="data/raw/unknown.csv",
        )