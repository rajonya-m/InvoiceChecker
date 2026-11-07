"""Reading files (CONCEPT: file handling, csv format, generators)."""
import csv

from invoiceguard.config import REQUIRED_COLUMNS
from invoiceguard.exceptions import FileFormatError


def read_csv_rows(path):
    """GENERATOR: hands back one (line_number, row) at a time.

    'yield' means we never load the whole file into memory.
    """
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise FileFormatError(f"CSV is missing columns: {missing}")

        for line_number, row in enumerate(reader, start=2):   # line 1 = header
            yield line_number, row
