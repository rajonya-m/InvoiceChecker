"""Command line entry point.

    python main.py data/invoices.csv
"""
import sys

from invoiceguard.database import InvoiceDB
from invoiceguard.exceptions import FileFormatError
from invoiceguard.logger_setup import get_logger
from invoiceguard.pipeline import run_pipeline
from invoiceguard.report import build_report, save_report

log = get_logger()


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path-to-invoices.csv>")
        return 1

    csv_path = sys.argv[1]
    with InvoiceDB() as db:
        try:
            stats = run_pipeline(csv_path, db)
        except FileNotFoundError:
            print(f"Error: file '{csv_path}' was not found.")
            return 1
        except FileFormatError as error:
            print(f"Error: {error}")
            return 1

        text_path, json_path = save_report(db, stats)
        print(build_report(db, stats))
        print(f"\nSaved: {text_path} and {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
