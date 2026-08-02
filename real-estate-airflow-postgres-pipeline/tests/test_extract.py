from unittest.mock import MagicMock, patch

import pytest

from etl.extract import extract


@patch("etl.extract.pd.read_csv")
def test_extract_reads_csv_and_returns_dataframe(mock_read_csv):
    # Arrange
    mock_df = MagicMock()
    mock_df.shape = (100, 12)
    mock_read_csv.return_value = mock_df

    file_path = "data/raw/test_data.csv"

    # Act
    result = extract(file_path, nrows=100)

    # Assert
    mock_read_csv.assert_called_once_with(file_path, nrows=100)
    assert result is mock_df


@patch("etl.extract.pd.read_csv")
def test_extract_raises_error_when_csv_read_fails(mock_read_csv):
    # Arrange
    mock_read_csv.side_effect = FileNotFoundError("CSV file not found")

    # Act and Assert
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        extract("data/raw/missing.csv")

    mock_read_csv.assert_called_once_with(
        "data/raw/missing.csv",
        nrows=None,
    )