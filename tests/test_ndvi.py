from typer.testing import CliRunner

from greensenti import app
from greensenti.cli.compute_index import app as compute_index_group

runner = CliRunner()


def test_ndvi_group():
    result = runner.invoke(app, ["compute-index", "ndvi", "--help"])
    assert result.exit_code == 0


def test_ndvi():
    result = runner.invoke(compute_index_group, ["ndvi", "tests/data/B04_10m.jp2", "tests/data/B08_10m.jp2"])
    assert result.exit_code == 0
