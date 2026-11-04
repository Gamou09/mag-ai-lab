import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from expense_tracker.storage import StorageError, load_expenses, save_expenses
from expense_tracker.tracker import ExpenseTracker


class TrackerTests(unittest.TestCase):
    def test_add_expense_stores_fields(self):
        tracker = ExpenseTracker()
        expense = tracker.add_expense("12.50", " Food ", " Lunch ")

        self.assertEqual(expense.amount, Decimal("12.50"))
        self.assertEqual(expense.category, "Food")
        self.assertEqual(expense.description, "Lunch")
        self.assertEqual(tracker.expenses, [expense])

    def test_invalid_input_is_rejected(self):
        tracker = ExpenseTracker()
        for amount in ["abc", "", "0", "-5", "NaN", "Infinity", "1e100"]:
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                tracker.add_expense(amount, "Food")

        with self.assertRaises(ValueError):
            tracker.add_expense("5", "   ")

        self.assertEqual(tracker.expenses, [])

    def test_total_is_exact(self):
        tracker = ExpenseTracker()
        self.assertEqual(tracker.total(), Decimal("0.00"))

        tracker.add_expense("0.10", "Food")
        tracker.add_expense("0.20", "Food")
        self.assertEqual(tracker.total(), Decimal("0.30"))


class StorageTests(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.path = Path(temp_dir.name) / "data" / "expenses.json"

    def test_missing_file_loads_empty(self):
        self.assertEqual(load_expenses(self.path), [])

    def test_save_and_load_round_trip(self):
        tracker = ExpenseTracker()
        tracker.add_expense("19.99", "Books", "Python guide")

        save_expenses(self.path, tracker.expenses)

        self.assertEqual(load_expenses(self.path), tracker.expenses)

    def test_corrupt_file_raises_storage_error(self):
        for content in ["not json", "[{}]", '[{"amount": "x", "category": "a", '
                        '"description": "b", "date": "c"}]']:
            with self.subTest(content=content):
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self.path.write_text(content, encoding="utf-8")
                with self.assertRaises(StorageError):
                    load_expenses(self.path)


if __name__ == "__main__":
    unittest.main()
