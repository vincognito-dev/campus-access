import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from campus_access import storage
from campus_access.cli import run_menu


class CliTests(unittest.TestCase):
    def setUp(self):
        # Isolated folder so the CLI never touches a real campus_requests.json
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        old_cwd = os.getcwd()
        os.chdir(self.tmp.name)
        self.addCleanup(os.chdir, old_cwd)
        # Start every test with an empty store
        storage._requests.clear()

    def run_cli(self, typed):
        inputs = iter(typed)
        with patch("builtins.input", side_effect=lambda prompt="": next(inputs)), \
             redirect_stdout(io.StringIO()) as captured:
            run_menu()
        return captured.getvalue()

    def test_cli_invalid_option_retries(self):
        output = self.run_cli(["junk", "quit", "n"])
        self.assertIn("Invalid option", output)
        # menu was shown again after the bad input
        self.assertEqual(output.count("Campus Access Card Manager"), 0 != 2)

    def test_cli_create_then_quit(self):
        output = self.run_cli(["1", "F011", "visitor", "quit", "n"])
        self.assertIn("created", output.lower())

    def test_cli_invalid_card_type_shows_error_and_retries(self):
        output = self.run_cli(["1", "F011", "banana", "quit", "n"])
        self.assertIn("Error", output)
        self.assertEqual(output.count("Campus Access Card Manager"), 2)


if __name__ == "__main__":
    unittest.main()