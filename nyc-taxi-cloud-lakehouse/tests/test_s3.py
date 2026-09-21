from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cloud.s3 import upload_file_to_s3


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