import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from campus_access.cli import run_menu


class CliTests(unittest.TestCase):
    def test_cli_invalid_option_retries(self):
        inputs = iter(["junk", "quit"])
        with patch("builtins.input", side_effect=lambda prompt="": next(inputs)), \
             redirect_stdout(io.StringIO()) as captured:
            run_menu()
        output = captured.getvalue()
        self.assertIn("Invalid option", output)

    def test_cli_create_then_quit(self):
        inputs = iter(["1", "F011", "visitor", "quit"])
        with patch("builtins.input", side_effect=lambda prompt="": next(inputs)), \
             redirect_stdout(io.StringIO()) as captured:
            run_menu()
        output = captured.getvalue()
        self.assertIn("created", output.lower())


if __name__ == "__main__":
    unittest.main()
