from unittest.mock import MagicMock, patch

import pytest

from cloud.glue import start_glue_crawler


def test_start_glue_crawler_success() -> None:
    mock_client = MagicMock()

    with patch(
        "cloud.glue.boto3.client",
        return_value=mock_client,
    ):
        start_glue_crawler(
            "nyc-taxi-processed-crawler"
        )

        mock_client.start_crawler.assert_called_once_with(
            Name="nyc-taxi-processed-crawler"
        )

def test_start_glue_crawler_uses_correct_region() -> None:
    mock_client = MagicMock()

    with patch(
        "cloud.glue.boto3.client",
        return_value=mock_client,
    ) as mock_boto_client:
        start_glue_crawler(
            "nyc-taxi-valid-crawler"
        )

        mock_boto_client.assert_called_once_with(
            "glue",
            region_name="us-east-1",
        )


def test_start_glue_crawler_rejects_empty_name() -> None:
    with pytest.raises(
        ValueError,
        match="crawler_name must not be empty",
    ):
        start_glue_crawler("")