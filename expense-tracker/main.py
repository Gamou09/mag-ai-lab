"""Entry point for the expense tracker. Run with: python3 main.py --help"""

import sys

from expense_tracker.cli import main

if __name__ == "__main__":
    sys.exit(main())
