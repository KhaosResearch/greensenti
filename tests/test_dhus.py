from unittest.mock import MagicMock

import pandas as pd
from pandas.testing import assert_frame_equal

from greensenti import dhus


def test_gcloud_path_is_valid():
    gcloud_path = dhus.get_gcloud_path("S2B_MSIL2A_20221005T105819_N0400_R094_T30SUF_20221005T135951")
    assert gcloud_path == "L2/tiles/30/S/UF/S2B_MSIL2A_20221005T105819_N0400_R094_T30SUF_20221005T135951.SAFE"


def test_copernicous_download_returns_correct_dataframe(monkeypatch):
    # Mock sentinelsat.sentinel.SentinelAPI.download_all
    mock = MagicMock()

    # Mock unzip
    monkeypatch.setattr(dhus, "unzip_product", lambda *args: None)

    status = list(dhus.copernicous_download(
        ids=[
            "uuid1",
            "uuid2",
            "uuid3",
            "uuid4",
            "uuid5",
        ],
        api=mock,
    ))

    expected_status = [
            {"uuid": "uuid1", "status": "ok"},
            {"uuid": "uuid2", "status": "ok"},
            {"uuid": "uuid3", "status": "ok"},
            {"uuid": "uuid4", "status": "ok"},
            {"uuid": "uuid5", "status": "ok"},
        ]

    assert status == expected_status
