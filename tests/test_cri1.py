from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as compute_index_group
from greensenti.cli.band_arithmetic import cri1

runner = CliRunner()


def test_cri1_cli_group():
    result = runner.invoke(app, ["compute-index", "cri1", "--help"])
    assert result.exit_code == 0


def test_cri1_cli():
    result = runner.invoke(compute_index_group, ["cri1", "tests/data/B1.jp2", "tests/data/B1.jp2"])
    assert result.exit_code == 0


def test_cri1():
    band = cri1(b2=Path("tests/data/B1.jp2"), b3=Path("tests/data/B1.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 1.0
