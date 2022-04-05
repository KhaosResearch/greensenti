from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group

runner = CliRunner()


def test_cloud_mask_group():
    result = runner.invoke(app, ["compute-index", "cloud-mask", "--help"])
    assert result.exit_code == 0


def test_cloud_mask_cli():
    result = runner.invoke(
        compute_index_group,
        ["cloud-mask", "tests/data/B1.jp2"],
    )
    assert result.exit_code == 0
