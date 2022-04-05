from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as compute_index_group
from greensenti.cli.band_arithmetic import evi2

runner = CliRunner()


def test_evi2_cli_group():
    result = runner.invoke(app, ["compute-index", "evi2", "--help"])
    assert result.exit_code == 0


def test_evi2_cli():
    result = runner.invoke(compute_index_group, ["evi2", "tests/data/B1.jp2", "tests/data/B2.jp2"])
    assert result.exit_code == 0


def test_evi2():
    band = evi2(
        b4=Path("tests/data/B1.jp2"),
        b8=Path("tests/data/B2.jp2"),
        output=None,
    )
    value = np.round(np.nanmean(band), decimals=1)
    assert value == np.float32(0.6)
