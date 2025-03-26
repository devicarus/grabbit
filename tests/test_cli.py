from click.testing import CliRunner
from grabbit.cli import cli
from grabbit.utils import get_version

def test_version():
    """ Tests the --version option """
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert result.output == get_version() + '\n'
