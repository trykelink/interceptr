# test_cli_version.py — Tests for the --version flag on the Interceptr CLI
from typer.testing import CliRunner

from interceptr import __version__
from interceptr.cli.main import app as cli_app

runner = CliRunner()


def test_version_flag_outputs_version():
    result = runner.invoke(cli_app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_version_flag_short_form():
    result = runner.invoke(cli_app, ["-V"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_version_output_format():
    result = runner.invoke(cli_app, ["--version"])
    assert f"interceptr {__version__}" in result.output
