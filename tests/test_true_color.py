from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group
from greensenti.cli.band_arithmetic import true_color

runner = CliRunner()


def test_true_color_group():
    result = runner.invoke(app, ["band-arithmetic", "true-color", "--help"])
    assert result.exit_code == 0


def test_true_color_cli():
    result = runner.invoke(
        band_arithmetic_group,
        ["true-color", "tests/data/B1.jp2", "tests/data/B2.jp2", "tests/data/B3.jp2"],
    )
    assert result.exit_code == 0


def test_true_color():
    tc = true_color(r=Path("tests/data/B1.jp2"), g=Path("tests/data/B2.jp2"), b=Path("tests/data/B3.jp2"), output=None)
    assert np.array_equal(tc, np.array([[[85, 170, 255]]]))
