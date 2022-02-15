from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group
from greensenti.cli.compute_index import ndre

runner = CliRunner()


def test_ndre_cli_group():
    result = runner.invoke(app, ["compute-index", "ndre", "--help"])
    assert result.exit_code == 0


def test_ndre_cli():
    result = runner.invoke(compute_index_group, ["ndre", "tests/data/B3.jp2", "tests/data/B1.jp2"])
    assert result.exit_code == 0


def test_ndre():
    band = ndre(b5=Path("tests/data/B1.jp2"), b9=Path("tests/data/B3.jp2"), output=None)
    value = np.nanmean(band)
    assert value == 0.5
