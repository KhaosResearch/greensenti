from typer.testing import CliRunner

from greensenti import app

runner = CliRunner()


def test_cli_run():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
