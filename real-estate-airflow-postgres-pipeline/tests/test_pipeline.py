from unittest.mock import patch
import pandas as pd
import pytest

from etl.pipeline import run_pipeline

@patch("etl.pipeline.load")
@patch("etl.pipeline.validate_data")
@patch("etl.pipeline.transform")
@patch("etl.pipeline.extract")
def test_run_pipeline_calls_all_steps(
    mock_extract,
    mock_transform,
    mock_validate_data,
    mock_load,
):
    df_raw = pd.DataFrame({"raw": [1]})
    df_clean = pd.DataFrame({"clean": [1]})

    mock_extract.return_value = df_raw
    mock_transform.return_value = df_clean

    run_pipeline()

    mock_extract.assert_called_once()
    mock_transform.assert_called_once_with(df_raw)
    mock_validate_data.assert_called_once_with(df_clean)
    mock_load.assert_called_once_with(df_clean)


@patch("etl.pipeline.load")
@patch("etl.pipeline.validate_data")
@patch("etl.pipeline.transform")
@patch("etl.pipeline.extract")
def test_run_pipeline_does_not_load_when_validation_fails(
    mock_extract,
    mock_transform,
    mock_validate_data,
    mock_load,
):
    df_raw = pd.DataFrame({"raw": [1]})
    df_clean = pd.DataFrame({"clean": [1]})

    mock_extract.return_value = df_raw
    mock_transform.return_value = df_clean
    mock_validate_data.side_effect = ValueError("Invalid data")

    with pytest.raises(ValueError, match="Invalid data"):
        run_pipeline()

    mock_load.assert_not_called()