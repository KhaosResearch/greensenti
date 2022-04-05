from pathlib import Path

import numpy as np
from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group
from greensenti.cli.band_arithmetic import evi2

runner = CliRunner()


def test_evi2_cli_group():
    result = runner.invoke(app, ["band-arithmetic", "evi2", "--help"])
    assert result.exit_code == 0


def test_evi2_cli():
    result = runner.invoke(band_arithmetic_group, ["evi2", "tests/data/B1.jp2", "tests/data/B2.jp2"])
    assert result.exit_code == 0


def test_evi2():
    band = evi2(
        b4=Path("tests/data/B1.jp2"),
        b8=Path("tests/data/B2.jp2"),
        output=None,
    )
    value = np.round(np.nanmean(band), decimals=1)
    assert value == np.float32(0.6)
