import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from expense_tracker.cli import main
from expense_tracker.storage import load_expenses


class CliTests(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.path = Path(temp_dir.name) / "expenses.json"

    def run_cli(self, *argv):
        """Return (exit code, stdout, stderr) for one CLI run."""
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(argv), data_file=self.path)
        return code, out.getvalue(), err.getvalue()

    def test_add_saves_expense(self):
        code, out, _ = self.run_cli("add", "12.50", "Food", "Lunch")

        self.assertEqual(code, 0)
        self.assertIn("Saved: 12.50 in Food", out)
        saved = load_expenses(self.path)
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].description, "Lunch")

    def test_description_is_optional(self):
        code, _, _ = self.run_cli("add", "5", "Food")

        self.assertEqual(code, 0)
        self.assertEqual(load_expenses(self.path)[0].description, "")

    def test_invalid_add_fails_without_saving(self):
        for args in [("abc", "Food"), ("-5", "Food"), ("5", "  ")]:
            with self.subTest(args=args):
                code, _, err = self.run_cli("add", *args)
                self.assertEqual(code, 1)
                self.assertIn("Error:", err)
                self.assertFalse(self.path.exists())

    def test_list_and_total_use_saved_data(self):
        self.run_cli("add", "12.50", "Food", "Lunch")
        self.run_cli("add", "7.25", "Transport", "Bus")

        _, listing, _ = self.run_cli("list")
        self.assertIn("Lunch", listing)
        self.assertIn("Bus", listing)

        _, total, _ = self.run_cli("total")
        self.assertIn("19.75", total)

    def test_list_when_empty(self):
        _, out, _ = self.run_cli("list")
        self.assertIn("No expenses yet.", out)

    def test_corrupt_file_is_reported_and_not_overwritten(self):
        self.path.write_text("not json", encoding="utf-8")

        code, _, err = self.run_cli("add", "5", "Food")

        self.assertEqual(code, 1)
        self.assertIn("Could not read", err)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "not json")

    def test_no_command_opens_menu(self):
        answers = ["1", "abc", "Food", "", "1", "3", "Food", "Snack", "3", "4"]
        with patch("builtins.input", side_effect=answers):
            code, out, _ = self.run_cli()

        self.assertEqual(code, 0)
        self.assertIn("is not a valid amount", out)
        self.assertIn("Total spending: 3.00", out)
        self.assertEqual(len(load_expenses(self.path)), 1)

    def test_menu_exits_cleanly_when_input_ends(self):
        with patch("builtins.input", side_effect=EOFError):
            code, out, _ = self.run_cli()

        self.assertEqual(code, 0)
        self.assertIn("Goodbye!", out)


if __name__ == "__main__":
    unittest.main()
