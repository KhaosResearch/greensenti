import numpy as np
import pytest
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group
from greensenti.cli.compute_index import ndwi

runner = CliRunner()


def test_ndwi_cli_group():
    result = runner.invoke(app, ["compute-index", "ndwi", "--help"])
    assert result.exit_code == 0


def test_ndwi_cli():
    result = runner.invoke(compute_index_group, ["ndwi", "tests/data/B03_10m.jp2", "tests/data/B08_10m.jp2"])
    assert result.exit_code == 0


def test_ndwi():
    band = ndwi(b3="tests/data/B03_10m.jp2", b8="tests/data/B08_10m.jp2", output=None)
    value = np.nanmean(band)
    assert value == pytest.approx(-0.345819)
