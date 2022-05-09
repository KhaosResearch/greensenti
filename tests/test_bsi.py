from pathlib import Path

import numpy as np
import pytest
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group
from greensenti.cli.band_arithmetic import bsi

runner = CliRunner()


def test_bsi_cli_group():
    result = runner.invoke(app, ["band-arithmetic", "bsi", "--help"])
    assert result.exit_code == 0


def test_bsi_cli():
    result = runner.invoke(band_arithmetic_group, ["bsi", "tests/data/B1.jp2", "tests/data/B2.jp2", "tests/data/B3.jp2", "tests/data/B3.jp2"])
    assert result.exit_code == 0


def test_bsi():
    band = bsi(b2=Path("tests/data/B1.jp2"), b4=Path("tests/data/B2.jp2"), b8=Path("tests/data/B3.jp2"), b11=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert pytest.approx(value, 0.000001) == 0.11111111