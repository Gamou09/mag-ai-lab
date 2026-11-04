# Expense Tracker

A simple command-line expense tracker. It uses only the Python standard library, so there is nothing to install.

## Features

- Add expenses with an amount, category and description
- View all expenses
- Calculate total spending
- Save automatically to `data/expenses.json` after each new expense

## Usage

Run these commands from this folder:

```
python3 main.py add 12.50 Food "Lunch with a client"   # description is optional
python3 main.py list
python3 main.py total
python3 main.py --help
```

Run with no command to open the interactive menu:

```
python3 main.py
```

## Tests

```
python3 -m unittest
```

## Project structure

```
expense-tracker/
├── main.py                  # Entry point
├── expense_tracker/
│   ├── cli.py               # Commands and interactive menu
│   ├── tracker.py           # Expense data and calculations
│   └── storage.py           # Load and save the JSON file
├── tests/
│   ├── test_cli.py
│   └── test_tracker.py
└── data/                    # Created on first save
    └── expenses.json
```
