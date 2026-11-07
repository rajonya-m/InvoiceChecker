"""Cleaning / enriching data (CONCEPT: transformation, dict lookup)."""
from invoiceguard.config import STATE_CODES


def transform(invoice):
    """Tidy the invoice and add new information to it."""
    invoice.vendor_name = invoice.vendor_name.title()      # "sharma steel" -> "Sharma Steel"
    invoice.amount = round(invoice.amount, 2)
    state_code = invoice.gstin[:2]                          # first 2 characters
    invoice.state = STATE_CODES.get(state_code, "Unknown")
    return invoice
