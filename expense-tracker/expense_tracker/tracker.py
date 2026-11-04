"""Core expense data and calculations."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

CENTS = Decimal("0.01")


def parse_amount(value):
    """Convert user input to a positive Decimal rounded to cents.

    Decimal is used instead of float so that totals stay exact
    (0.10 + 0.20 is 0.30, not 0.30000000000000004).
    """
    try:
        amount = Decimal(str(value).strip())
        # Decimal accepts "NaN" and "Infinity", which are not usable amounts.
        if not amount.is_finite():
            raise InvalidOperation
        # Also raises InvalidOperation if the value is too large, e.g. "1e100".
        amount = amount.quantize(CENTS)
    except InvalidOperation:
        raise ValueError(f"'{value}' is not a valid amount.") from None

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return amount


@dataclass
class Expense:
    amount: Decimal
    category: str
    description: str
    date: str

    def to_dict(self):
        return {
            "amount": str(self.amount),
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            amount=Decimal(data["amount"]),
            category=data["category"],
            description=data["description"],
            date=data["date"],
        )


class ExpenseTracker:
    def __init__(self, expenses=None):
        self.expenses = list(expenses) if expenses else []

    def add_expense(self, amount, category, description=""):
        category = category.strip()
        if not category:
            raise ValueError("Category cannot be empty.")

        expense = Expense(
            amount=parse_amount(amount),
            category=category,
            description=description.strip(),
            date=date.today().isoformat(),
        )
        self.expenses.append(expense)
        return expense

    def total(self):
        return sum((expense.amount for expense in self.expenses), Decimal("0.00"))
