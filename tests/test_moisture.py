from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as compute_index_group
from greensenti.cli.band_arithmetic import moisture

runner = CliRunner()


def test_moisture_cli_group():
    result = runner.invoke(app, ["compute-index", "moisture", "--help"])
    assert result.exit_code == 0


def test_moisture_cli():
    result = runner.invoke(compute_index_group, ["moisture", "tests/data/B3.jp2", "tests/data/B1.jp2"])
    assert result.exit_code == 0


def test_moisture():
    band = moisture(b8a=Path("tests/data/B3.jp2"), b11=Path("tests/data/B1.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5
