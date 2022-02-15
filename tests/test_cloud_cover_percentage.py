from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group

runner = CliRunner()


def test_cloud_cover_percentage_group():
    result = runner.invoke(app, ["compute-index", "cloud-cover-percentage", "--help"])
    assert result.exit_code == 0


def test_cloud_cover_percentage():
    result = runner.invoke(
        compute_index_group,
        ["cloud-cover-percentage", "tests/data/B03_20m.jp2", "tests/data/B04_20m.jp2", "tests/data/B11_20m.jp2"],
    )
    assert result.exit_code == 0
