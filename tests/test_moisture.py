from pathlib import Path

import numpy as np
import pytest
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group
from greensenti.cli.compute_index import moisture

runner = CliRunner()


def test_moisture_cli_group():
    result = runner.invoke(app, ["compute-index", "moisture", "--help"])
    assert result.exit_code == 0


def test_moisture_cli():
    result = runner.invoke(compute_index_group, ["moisture", "tests/data/B8A_60m.jp2", "tests/data/B11_60m.jp2"])
    assert result.exit_code == 0


def test_moisture():
    band = moisture(b8a=Path("tests/data/B8A_60m.jp2"), b11=Path("tests/data/B11_60m.jp2"), output=None)
    value = np.nanmean(band)
    assert value == pytest.approx(0.09322458)
