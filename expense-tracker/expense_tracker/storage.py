"""Load and save expenses as a JSON file."""

import json
import os
from decimal import InvalidOperation
from pathlib import Path

from expense_tracker.tracker import Expense


class StorageError(Exception):
    """The data file exists but could not be read."""


def load_expenses(path):
    path = Path(path)
    if not path.exists():
        return []

    try:
        with path.open(encoding="utf-8") as file:
            return [Expense.from_dict(item) for item in json.load(file)]
    except (OSError, ValueError, KeyError, TypeError, InvalidOperation) as error:
        raise StorageError(f"Could not read {path}: {error}") from error


def save_expenses(path, expenses):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file first so that a crash mid-save
    # cannot leave the real data file half-written.
    temp_path = path.with_name(path.name + ".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump([expense.to_dict() for expense in expenses], file, indent=2)
    os.replace(temp_path, path)
