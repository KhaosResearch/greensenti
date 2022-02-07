from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group

runner = CliRunner()


def test_true_color_group():
    result = runner.invoke(app, ["compute-index", "true-color", "--help"])
    assert result.exit_code == 0


def test_true_color():
    result = runner.invoke(
        compute_index_group,
        ["true-color", "tests/data/B04_10m.jp2", "tests/data/B03_10m.jp2", "tests/data/B02_10m.jp2"],
    )
    assert result.exit_code == 0
