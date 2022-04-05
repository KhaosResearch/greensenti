from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.band_arithmetic import app as band_arithmetic_group

runner = CliRunner()


def test_cloud_cover_percentage_group():
    result = runner.invoke(app, ["band-arithmetic", "cloud-cover-percentage", "--help"])
    assert result.exit_code == 0


def test_cloud_cover_percentage_cli():
    result = runner.invoke(
        band_arithmetic_group,
        ["cloud-cover-percentage", "tests/data/B1.jp2", "tests/data/B2.jp2", "tests/data/B3.jp2"],
    )
    assert result.exit_code == 0
