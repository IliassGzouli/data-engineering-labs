import polars as pl
import pytest

from ingestion.extract import extract_csv

def test_extract_csv_returns_expected_dataframe(tmp_path):
    #arrange
    csv_file = tmp_path / "orders.csv"

    csv_file.write_text(
        "order_id,order_status\n"
        "order_001,delivered\n"
        "order_002,shipped\n",
        encoding="utf-8",
    )

    #act
    result = extract_csv(csv_file)

    #assert
    assert isinstance(result, pl.DataFrame)
    assert result.height == 2
    assert result.width == 2
    assert result.columns == ["order_id","order_status"]

def test_extract_csv_raises_error_when_file_not_exist(tmp_path):
    #arrange 
    missing_file = tmp_path / "missing.csv"

    #act and assert
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        extract_csv(missing_file)

def test_extract_csv_rejects_non_csv_file(tmp_path):
    # Arrange
    text_file = tmp_path / "orders.txt"
    text_file.write_text("test", encoding="utf-8")

    # Act and Assert
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_csv(text_file)


def test_extract_csv_rejects_empty_file(tmp_path):
    # Arrange
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")

    # Act and Assert
    with pytest.raises(ValueError, match="CSV file is empty"):
        extract_csv(empty_file)

def test_extract_csv_rejects_header_only_file(tmp_path):
    # Arrange
    header_only_file = tmp_path / "orders.csv"
    header_only_file.write_text(
        "order_id,order_status\n",
        encoding="utf-8",
    )

    # Act and Assert
    with pytest.raises(ValueError, match="contains no data rows"):
        extract_csv(header_only_file)