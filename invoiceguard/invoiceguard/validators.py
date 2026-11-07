"""Validation (CONCEPT: regex, functions, exceptions, control flow)."""
import re
from datetime import datetime

from invoiceguard.exceptions import InvoiceValidationError
from invoiceguard.models import Invoice

# Regex patterns. Compiled once, used many times.
INVOICE_NO_PATTERN = re.compile(r"^INV-\d{4}-\d{3,5}$")           # INV-2026-001
GSTIN_PATTERN = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


def is_valid_gstin(value):
    return bool(GSTIN_PATTERN.match(value))


def parse_amount(text):
    """'1,250.50' -> 1250.5   (raises ValueError if it is not a number)"""
    return float(text.replace(",", "").strip())


def parse_date(text):
    """'2026-10-05' -> a date object (raises ValueError if impossible)."""
    return datetime.strptime(text.strip(), "%Y-%m-%d").date()


def validate_row(row):
    """Check one CSV row. Returns an Invoice, or raises InvoiceValidationError
    that lists EVERY problem found (not just the first)."""
    errors = []

    invoice_no = (row.get("invoice_no") or "").strip().upper()
    vendor = (row.get("vendor_name") or "").strip()
    gstin = (row.get("gstin") or "").strip().upper()
    email = (row.get("email") or "").strip().lower()
    description = (row.get("description") or "").strip()
    invoice_date = None
    amount = None

    if not INVOICE_NO_PATTERN.match(invoice_no):
        errors.append(f"invalid invoice number '{invoice_no}'")
    if not vendor:
        errors.append("vendor name is missing")
    if not is_valid_gstin(gstin):
        errors.append(f"invalid GSTIN '{gstin}'")
    if not EMAIL_PATTERN.match(email):
        errors.append(f"invalid email '{email}'")

    try:
        invoice_date = parse_date(row.get("invoice_date") or "")
    except ValueError:
        errors.append(f"invalid date '{row.get('invoice_date')}'")

    try:
        amount = parse_amount(row.get("amount") or "")
        if amount <= 0:
            errors.append(f"amount must be positive, got {amount}")
    except ValueError:
        errors.append(f"invalid amount '{row.get('amount')}'")

    if errors:
        raise InvoiceValidationError(errors)

    return Invoice(invoice_no, vendor, gstin, invoice_date, amount,
                   email, description)
