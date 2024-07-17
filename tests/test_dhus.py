from unittest.mock import MagicMock, patch

import pandas as pd
from greensenti import dhus


def test_gcloud_path_is_valid():
    gcloud_path = dhus.get_gcloud_path("S2B_MSIL2A_20221005T105819_N0400_R094_T30SUF_20221005T135951")
    assert gcloud_path == "L2/tiles/30/S/UF/S2B_MSIL2A_20221005T105819_N0400_R094_T30SUF_20221005T135951.SAFE"


def test_copernicous_download_returns_correct_dataframe():
    # Sample data to be returned by the mocked response
    mock_response = {
        "value": [
            {"Name": "S2A_MSIL2A_20210101T000000_N0214_R000_T00X00_20210101T000000", "OtherField": "value1"},
            {"Name": "S2B_MSIL2A_20210102T000000_N0214_R000_T00X00_20210102T000000", "OtherField": "value2"},
        ]
    }

    # Mock unzip
    with patch("requests.get") as mock_get:
        # Configure the mock to return a response with our mock_response JSON data
        mock_get.return_value.json = MagicMock(return_value=mock_response)

        result = dhus.get_metadata_cdse(
            footprint="POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))",
            from_date="2021-01-01",
            to_date="2021-01-02",
        )

    # Verify the response
    assert isinstance(result, pd.DataFrame)
    assert result.shape[0] == len(mock_response["value"])
    assert "title" in result.columns
    assert "OtherField" in result.columns
    assert result["title"].to_list() == [x["Name"] for x in mock_response["value"]]
