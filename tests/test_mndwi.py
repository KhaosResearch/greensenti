from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group
from greensenti.cli.band_arithmetic import mndwi

runner = CliRunner()


def test_mndwi_cli_group():
    result = runner.invoke(app, ["band-arithmetic", "mndwi", "--help"])
    assert result.exit_code == 0


def test_mndwi_cli():
    result = runner.invoke(band_arithmetic_group, ["mndwi", "tests/data/B1.jp2", "tests/data/B2.jp2"])
    assert result.exit_code == 0


def test_mndwi():
    band = mndwi(b3=Path("tests/data/B3.jp2"), b11=Path("tests/data/B1.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5
