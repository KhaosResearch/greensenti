from pathlib import Path

import numpy as np
import pytest
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group
from greensenti.cli.compute_index import ndsi

runner = CliRunner()


def test_ndsi_cli_group():
    result = runner.invoke(app, ["compute-index", "ndsi", "--help"])
    assert result.exit_code == 0


def test_ndsi_cli():
    result = runner.invoke(compute_index_group, ["ndsi", "tests/data/B03_20m.jp2", "tests/data/B11_20m.jp2"])
    assert result.exit_code == 0


def test_ndsi():
    band = ndsi(b3=Path("tests/data/B03_20m.jp2"), b11=Path("tests/data/B11_20m.jp2"), output=None)
    value = np.nanmean(band)
    assert value == pytest.approx(0.905018)
