from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group
from greensenti.cli.band_arithmetic import bri

runner = CliRunner()


def test_bri_cli_group():
    result = runner.invoke(app, ["band-arithmetic", "bri", "--help"])
    assert result.exit_code == 0


def test_bri_cli():
    result = runner.invoke(band_arithmetic_group, ["bri", "tests/data/B1.jp2", "tests/data/B2.jp2", "tests/data/B3.jp2"])
    assert result.exit_code == 0


def test_bri():
    band = bri(
        b3=Path("tests/data/B1.jp2"),
        b5=Path("tests/data/B2.jp2"),
        b8=Path("tests/data/B3.jp2"),
        output=None,
    )
    value = np.round(np.nanmean(band), decimals=3)
    assert value == np.float32(0.167)
