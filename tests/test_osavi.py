from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group
from greensenti.cli.band_arithmetic import osavi

runner = CliRunner()


def test_osavi_cli_group():
    result = runner.invoke(app, ["band-arithmetic", "osavi", "--help"])
    assert result.exit_code == 0


def test_osavi_cli():
    result = runner.invoke(band_arithmetic_group, ["osavi", "tests/data/B1.jp2", "tests/data/B2.jp2"])
    assert result.exit_code == 0


def test_osavi():
    band = osavi(b4=Path("tests/data/B1.jp2"), b8=Path("tests/data/B2.jp2"), Y=0.16, output=None)
    value = np.round(np.nanmean(band), decimals=3)
    assert value == np.float32(0.367)
