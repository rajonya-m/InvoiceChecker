import pytest

from invoiceguard.exceptions import InvoiceValidationError
from invoiceguard.validators import (is_valid_gstin, parse_amount, parse_date,
                                     validate_row)

GOOD_ROW = {"invoice_no": "INV-2026-001", "vendor_name": "Acme", "gstin": "19ABCDE1234F1Z5",
            "invoice_date": "2026-10-05", "amount": "1,200.50",
            "email": "a@b.com", "description": "x"}


def test_gstin_regex():
    assert is_valid_gstin("19ABCDE1234F1Z5")
    assert not is_valid_gstin("12345")
    assert not is_valid_gstin("19abcde1234f1z5")      # must be upper case


def test_parse_amount_removes_commas():
    assert parse_amount("1,250.50") == 1250.5


def test_parse_date_rejects_impossible_date():
    with pytest.raises(ValueError):
        parse_date("2026-13-45")


def test_valid_row_becomes_invoice():
    inv = validate_row(GOOD_ROW)
    assert inv.amount == 1200.5 and inv.invoice_no == "INV-2026-001"


def test_all_errors_are_collected():
    bad = dict(GOOD_ROW, gstin="x", email="bad", amount="-5")
    with pytest.raises(InvoiceValidationError) as info:
        validate_row(bad)
    assert len(info.value.errors) == 3
