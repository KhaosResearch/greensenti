from pathlib import Path

import numpy as np
import pytest

from greensenti.band_arithmetic import *


def test_bri():
    band = bri(
        b3=Path("tests/data/B1.jp2"),
        b5=Path("tests/data/B2.jp2"),
        b8=Path("tests/data/B3.jp2"),
        output=None,
    )
    value = np.round(np.nanmean(band), decimals=3)
    assert value == np.float32(0.167)


def test_cloud_cover_percentage():
    result = cloud_cover_percentage(
        b3=Path("tests/data/B1.jp2"), b4=Path("tests/data/B2.jp2"), b11=Path("tests/data/B3.jp2"), tau=0.2, output=None
    )
    assert result == 0.0


def test_cloud_mask():
    mask = cloud_mask(scl=Path("tests/data/B1.jp2"), output=None)
    value = np.round(np.nanmean(mask), decimals=3)
    assert value == 0.0


def test_cri1():
    band = cri1(b2=Path("tests/data/B1.jp2"), b3=Path("tests/data/B1.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 1.0


def test_evi():
    band = evi(
        b2=Path("tests/data/B1.jp2"),
        b4=Path("tests/data/B2.jp2"),
        b8=Path("tests/data/B3.jp2"),
        output=None,
    )
    value = np.round(np.nanmean(band), decimals=3)
    assert value == np.float32(0.294)


def test_evi2():
    band = evi2(
        b4=Path("tests/data/B1.jp2"),
        b8=Path("tests/data/B2.jp2"),
        output=None,
    )
    value = np.round(np.nanmean(band), decimals=1)
    assert value == np.float32(0.6)


def test_mndwi():
    band = mndwi(b3=Path("tests/data/B3.jp2"), b11=Path("tests/data/B1.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5


def test_moisture():
    band = moisture(b8a=Path("tests/data/B3.jp2"), b11=Path("tests/data/B1.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5


def test_ndre():
    band = ndre(b5=Path("tests/data/B1.jp2"), b9=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5


def test_ndsi():
    band = ndsi(b3=Path("tests/data/B1.jp2"), b11=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.0


def test_ndvi():
    band = ndvi(b4=Path("tests/data/B1.jp2"), b8=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5


def test_ndwi():
    band = ndwi(b3=Path("tests/data/B3.jp2"), b8=Path("tests/data/B1.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5


def test_ndyi():
    band = ndyi(b2=Path("tests/data/B1.jp2"), b3=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5


def test_osavi():
    band = osavi(b4=Path("tests/data/B1.jp2"), b8=Path("tests/data/B2.jp2"), Y=0.16, output=None)
    value = np.round(np.nanmean(band), decimals=3)
    assert value == np.float32(0.367)


def test_ri():
    band = ri(b3=Path("tests/data/B1.jp2"), b4=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5


def test_true_color():
    tc = true_color(r=Path("tests/data/B1.jp2"), g=Path("tests/data/B2.jp2"), b=Path("tests/data/B3.jp2"), output=None)
    assert np.array_equal(tc, np.array([[[85]], [[170]], [[255]]]))


def test_bsi():
    band = bsi(
        b2=Path("tests/data/B1.jp2"),
        b4=Path("tests/data/B2.jp2"),
        b8=Path("tests/data/B3.jp2"),
        b11=Path("tests/data/B3.jp2"),
        output=None,
    )
    value = np.nanmean(band)
    assert pytest.approx(value, 0.000001) == 0.11111111
