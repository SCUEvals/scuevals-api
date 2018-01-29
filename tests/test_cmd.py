import unittest
from click.testing import CliRunner

from scuevals_api.cmd import cli


class CmdsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

        def cli_run(self, *cmds):
            return self.runner.invoke(cli, cmds)

        cls.cli_run = cli_run

    def test_initdb(self):
        result = self.cli_run('initdb')
        self.assertEqual(0, result.exit_code, msg=result.output)
