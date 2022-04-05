from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as compute_index_group
from greensenti.cli.band_arithmetic import ndwi

runner = CliRunner()


def test_ndwi_cli_group():
    result = runner.invoke(app, ["compute-index", "ndwi", "--help"])
    assert result.exit_code == 0


def test_ndwi_cli():
    result = runner.invoke(compute_index_group, ["ndwi", "tests/data/B3.jp2", "tests/data/B1.jp2"])
    assert result.exit_code == 0


def test_ndwi():
    band = ndwi(b3=Path("tests/data/B3.jp2"), b8=Path("tests/data/B1.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5
