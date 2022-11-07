from unittest.mock import MagicMock

import pandas as pd
from pandas.testing import assert_frame_equal

from greensenti import dhus


def test_gcloud_path_is_valid():
    gcloud_path = dhus.get_gcloud_path("S2B_MSIL2A_20221005T105819_N0400_R094_T30SUF_20221005T135951")
    assert gcloud_path == "L2/tiles/30/S/UF/S2B_MSIL2A_20221005T105819_N0400_R094_T30SUF_20221005T135951.SAFE"


def test_copernicous_download_returns_correct_dataframe():
    # Mock sentinelsat.sentinel.SentinelAPI.download_all
    mock = MagicMock()
    mock.download_all.return_value = (
        ["uuid1", "uuid5"],
        ["uuid2"],
        ["uuid3", "uuid4"],
    )

    status_df = dhus.copernicous_download(
        ids=[
            "uuid1",
            "uuid2",
            "uuid3",
            "uuid4",
            "uuid5",
        ],
        api=mock,
    )

    expected_status = pd.DataFrame(
        [
            {"uuid": "uuid1", "status": "ok"},
            {"uuid": "uuid5", "status": "ok"},
            {"uuid": "uuid2", "status": "triggered"},
            {"uuid": "uuid3", "status": "failed"},
            {"uuid": "uuid4", "status": "failed"},
        ]
    )

    assert_frame_equal(status_df, expected_status)
