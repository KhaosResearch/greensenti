from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group

runner = CliRunner()


def test_cloud_mask_group():
    result = runner.invoke(app, ["band-arithmetic", "cloud-mask", "--help"])
    assert result.exit_code == 0


def test_cloud_mask_cli():
    result = runner.invoke(
        band_arithmetic_group,
        ["cloud-mask", "tests/data/B1.jp2"],
    )
    assert result.exit_code == 0
