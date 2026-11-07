from datetime import date

from invoiceguard.models import Invoice
from invoiceguard.rules import (DuplicateBillingRule, NearApprovalLimitRule,
                                RoundAmountRule, WeekendInvoiceRule,
                                build_default_rules, risk_level_for, score_invoice)


def make(amount=1000.0, day=date(2026, 10, 5), gstin="19ABCDE1234F1Z5"):
    return Invoice("INV-2026-001", "Acme", gstin, day, amount, "a@b.com")


def test_near_limit():
    rule = NearApprovalLimitRule()
    assert rule.check(make(49500))
    assert not rule.check(make(40000))
    assert not rule.check(make(50000))      # at the limit is not "just below"


def test_round_amount():
    assert RoundAmountRule().check(make(80000))
    assert not RoundAmountRule().check(make(80500))
    assert not RoundAmountRule().check(make(5000))     # too small to matter


def test_weekend():
    assert WeekendInvoiceRule().check(make(day=date(2026, 10, 10)))     # Saturday
    assert not WeekendInvoiceRule().check(make(day=date(2026, 10, 5)))  # Monday


def test_duplicate_billing_needs_two_invoices():
    rule = DuplicateBillingRule()
    assert rule.check(make(500)) is False
    assert rule.check(make(500)) is True


def test_score_and_level():
    inv = score_invoice(make(200000, date(2026, 10, 24)), build_default_rules())
    assert set(inv.flags) == {"ROUND_AMOUNT", "WEEKEND", "HIGH_VALUE"}
    assert inv.risk_score == 50 and inv.risk_level == "High"


def test_risk_levels():
    assert risk_level_for(0) == "Low"
    assert risk_level_for(25) == "Medium"
    assert risk_level_for(50) == "High"
