"""Command-line interface: direct commands plus an interactive menu."""

import argparse
import sys
from pathlib import Path

from expense_tracker.storage import StorageError, load_expenses, save_expenses
from expense_tracker.tracker import ExpenseTracker

DATA_FILE = Path(__file__).parent.parent / "data" / "expenses.json"

MENU = """
=== Expense Tracker ===
1. Add expense
2. View all expenses
3. Show total spending
4. Exit"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Track your expenses. Run with no command to open the menu.",
    )
    commands = parser.add_subparsers(dest="command", title="commands")

    add = commands.add_parser("add", help="add a new expense")
    add.add_argument("amount", help="amount spent, e.g. 12.50")
    add.add_argument("category", help="category, e.g. Food")
    add.add_argument("description", nargs="?", default="", help="optional description")

    commands.add_parser("list", help="view all expenses")
    commands.add_parser("total", help="show total spending")
    return parser


def add_expense(tracker, data_file, amount, category, description):
    expense = tracker.add_expense(amount, category, description)
    save_expenses(data_file, tracker.expenses)
    print(f"Saved: {expense.amount:.2f} in {expense.category}")


def print_expenses(tracker):
    if not tracker.expenses:
        print("No expenses yet.")
        return

    print(f"{'Date':<12}{'Amount':>10}  {'Category':<16}Description")
    print("-" * 60)
    for expense in tracker.expenses:
        print(
            f"{expense.date:<12}{expense.amount:>10.2f}  "
            f"{expense.category:<16}{expense.description}"
        )


def print_total(tracker):
    print(f"Total spending: {tracker.total():.2f}")


def run_menu(tracker, data_file):
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            amount = input("Amount: ")
            category = input("Category: ")
            description = input("Description: ")
            try:
                add_expense(tracker, data_file, amount, category, description)
            except ValueError as error:
                # Bad input should not end the session; let the user try again.
                print(f"Error: {error}")
        elif choice == "2":
            print_expenses(tracker)
        elif choice == "3":
            print_total(tracker)
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Please choose 1, 2, 3 or 4.")


def main(argv=None, data_file=DATA_FILE):
    """Run the CLI and return a process exit code."""
    args = build_parser().parse_args(argv)

    try:
        # If the file is unreadable this stops here rather than starting
        # empty, which would overwrite the existing file on the next save.
        tracker = ExpenseTracker(load_expenses(data_file))

        if args.command == "add":
            add_expense(tracker, data_file, args.amount, args.category, args.description)
        elif args.command == "list":
            print_expenses(tracker)
        elif args.command == "total":
            print_total(tracker)
        else:
            run_menu(tracker, data_file)
    except (ValueError, StorageError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")

    return 0
