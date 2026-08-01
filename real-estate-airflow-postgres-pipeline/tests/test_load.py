from unittest.mock import MagicMock, patch

from config import DATABASE_URL, POSTGRES_TABLE_NAME
from etl.load import load

@patch("etl.load.create_engine")
def test_load_writes_dataframe_to_postgres(mock_create_engine):

    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    mock_df = MagicMock()
    mock_df.shape = (100, 11)


    load(mock_df)

    mock_create_engine.assert_called_once_with(DATABASE_URL)

    mock_df.to_sql.assert_called_once_with(
        POSTGRES_TABLE_NAME,
        mock_engine,
        if_exists="replace",
        index=False,
        chunksize=10000,
    )


import pytest
from unittest.mock import MagicMock, patch

from etl.load import load


@patch("etl.load.create_engine")
def test_load_raises_error_when_database_write_fails(mock_create_engine):
    # Arrange
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    mock_df = MagicMock()
    mock_df.shape = (100, 11)
    mock_df.to_sql.side_effect = RuntimeError("Database write failed")

    # Act and Assert
    with pytest.raises(RuntimeError, match="Database write failed"):
        load(mock_df)

    mock_df.to_sql.assert_called_once()