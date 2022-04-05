from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group
from greensenti.cli.band_arithmetic import ri

runner = CliRunner()


def test_ri_cli_group():
    result = runner.invoke(app, ["band-arithmetic", "ri", "--help"])
    assert result.exit_code == 0


def test_ndsi_cli():
    result = runner.invoke(band_arithmetic_group, ["ri", "tests/data/B1.jp2", "tests/data/B3.jp2"])
    assert result.exit_code == 0


def test_ndsi():
    band = ri(b3=Path("tests/data/B1.jp2"), b4=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5
