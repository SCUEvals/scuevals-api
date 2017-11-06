import unittest
from click.testing import CliRunner
from flask.cli import ScriptInfo

from scuevals_api import create_app
from scuevals_api.cmd import cli


class CmdsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()
        obj = ScriptInfo(create_app=create_app)

        def cli_run(self, *cmds):
            return self.runner.invoke(cli, cmds, obj=obj)

        cls.cli_run = cli_run

    def test_initdb(self):
        result = self.cli_run('initdb')
        self.assertEqual(0, result.exit_code)

    def test_seeddb(self):
        result = self.cli_run('seeddb')
        self.assertEqual(0, result.exit_code)

