from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group
from greensenti.cli.band_arithmetic import ndsi

runner = CliRunner()


def test_ndsi_cli_group():
    result = runner.invoke(app, ["band-arithmetic", "ndsi", "--help"])
    assert result.exit_code == 0


def test_ndsi_cli():
    result = runner.invoke(band_arithmetic_group, ["ndsi", "tests/data/B3.jp2", "tests/data/B1.jp2"])
    assert result.exit_code == 0


def test_ndsi():
    band = ndsi(b3=Path("tests/data/B1.jp2"), b11=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.0
