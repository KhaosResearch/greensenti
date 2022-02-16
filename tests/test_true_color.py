from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group
from greensenti.cli.compute_index import true_color

runner = CliRunner()


def test_true_color_group():
    result = runner.invoke(app, ["compute-index", "true-color", "--help"])
    assert result.exit_code == 0


def test_true_color_cli():
    result = runner.invoke(
        compute_index_group,
        ["true-color", "tests/data/B1.jp2", "tests/data/B2.jp2", "tests/data/B3.jp2"],
    )
    assert result.exit_code == 0


def test_true_color():
    tc = true_color(r=Path("tests/data/B1.jp2"), g=Path("tests/data/B2.jp2"), b=Path("tests/data/B3.jp2"), output=None)
    assert np.array_equal(tc, np.array([[[85, 170, 255]]]))
