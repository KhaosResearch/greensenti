from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group
from greensenti.cli.compute_index import evi

runner = CliRunner()


def test_evi_cli_group():
    result = runner.invoke(app, ["compute-index", "evi", "--help"])
    assert result.exit_code == 0


def test_evi_cli():
    result = runner.invoke(compute_index_group, ["evi", "tests/data/B1.jp2", "tests/data/B2.jp2", "tests/data/B3.jp2"])
    assert result.exit_code == 0


def test_evi():
    band = evi(
        b2=Path("tests/data/B1.jp2"),
        b4=Path("tests/data/B2.jp2"),
        b8=Path("tests/data/B3.jp2"),
        output=None,
    )
    value = np.round(np.nanmean(band), decimals=3)
    assert value == np.float32(0.294)
