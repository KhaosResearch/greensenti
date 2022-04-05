from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group
from greensenti.cli.band_arithmetic import ndre

runner = CliRunner()


def test_ndre_cli_group():
    result = runner.invoke(app, ["band-arithmetic", "ndre", "--help"])
    assert result.exit_code == 0


def test_ndre_cli():
    result = runner.invoke(band_arithmetic_group, ["ndre", "tests/data/B3.jp2", "tests/data/B1.jp2"])
    assert result.exit_code == 0


def test_ndre():
    band = ndre(b5=Path("tests/data/B1.jp2"), b9=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5
