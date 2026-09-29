from pathlib import Path
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

import pytest

from cloud.s3 import upload_file_to_s3, s3_object_exists


def test_upload_file_to_s3_success(tmp_path: Path) -> None:
    local_file = tmp_path / "sample.parquet"
    local_file.write_text("test data")

    mock_client = MagicMock()

    with patch(
        "cloud.s3.boto3.client",
        return_value=mock_client,
    ):
        upload_file_to_s3(
            local_path=local_file,
            bucket_name="test-bucket",
            object_key="raw/sample.parquet",
        )

        mock_client.upload_file.assert_called_once()

        args, kwargs = mock_client.upload_file.call_args

        assert args[0] == str(local_file)
        assert args[1] == "test-bucket"
        assert args[2] == "raw/sample.parquet"
        assert "Config" in kwargs


def test_upload_file_to_s3_missing_file(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.parquet"

    with pytest.raises(FileNotFoundError):
        upload_file_to_s3(
            local_path=missing_file,
            bucket_name="test-bucket",
            object_key="raw/missing.parquet",
        )


def test_upload_file_to_s3_directory(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "data"
    directory.mkdir()

    with pytest.raises(ValueError):
        upload_file_to_s3(
            local_path=directory,
            bucket_name="test-bucket",
            object_key="raw/data",
        )

# test exist object
def test_s3_object_exists_returns_true() -> None:
    mock_client = MagicMock()

    with patch(
        "cloud.s3.boto3.client",
        return_value=mock_client,
    ):
        result = s3_object_exists(
            bucket_name="test-bucket",
            object_key="raw/sample.parquet",
        )

    assert result is True

    mock_client.head_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="raw/sample.parquet",
    )


def test_s3_object_exists_returns_false_for_404() -> None:
    mock_client = MagicMock()

    mock_client.head_object.side_effect = ClientError(
        {
            "Error": {
                "Code": "404",
                "Message": "Not Found",
            }
        },
        "HeadObject",
    )

    with patch(
        "cloud.s3.boto3.client",
        return_value=mock_client,
    ):
        result = s3_object_exists(
            bucket_name="test-bucket",
            object_key="raw/missing.parquet",
        )

    assert result is False


def test_s3_object_exists_raises_for_other_errors() -> None:
    mock_client = MagicMock()

    mock_client.head_object.side_effect = ClientError(
        {
            "Error": {
                "Code": "403",
                "Message": "Access Denied",
            }
        },
        "HeadObject",
    )

    with patch(
        "cloud.s3.boto3.client",
        return_value=mock_client,
    ):
        with pytest.raises(ClientError):
            s3_object_exists(
                bucket_name="test-bucket",
                object_key="raw/sample.parquet",
            )