"""Red-flag rules (CONCEPT: inheritance, polymorphism, list comprehension)."""
from invoiceguard.config import (APPROVAL_LIMIT, HIGH_VALUE_LIMIT,
                                 NEAR_LIMIT_BAND, ROUND_AMOUNT_MIN)


class RedFlagRule:
    """Parent class. Every rule has a code, points, and a check() method."""
    code = "BASE"
    description = ""
    points = 0

    def check(self, invoice):
        """Return True if the invoice breaks this rule."""
        raise NotImplementedError("Child classes must write their own check()")


class NearApprovalLimitRule(RedFlagRule):
    code = "NEAR_LIMIT"
    description = "Amount sits just below the approval limit (possible splitting)"
    points = 25

    def check(self, invoice):
        lower = APPROVAL_LIMIT * (1 - NEAR_LIMIT_BAND)
        return lower <= invoice.amount < APPROVAL_LIMIT


class RoundAmountRule(RedFlagRule):
    code = "ROUND_AMOUNT"
    description = "Suspiciously round amount"
    points = 10

    def check(self, invoice):
        return invoice.amount >= ROUND_AMOUNT_MIN and invoice.amount % 1000 == 0


class WeekendInvoiceRule(RedFlagRule):
    code = "WEEKEND"
    description = "Invoice dated on a Saturday or Sunday"
    points = 15

    def check(self, invoice):
        return invoice.invoice_date.weekday() >= 5      # Mon=0 ... Sat=5, Sun=6


class HighValueRule(RedFlagRule):
    code = "HIGH_VALUE"
    description = "Very high value invoice"
    points = 25

    def check(self, invoice):
        return invoice.amount >= HIGH_VALUE_LIMIT


class DuplicateBillingRule(RedFlagRule):
    """Same vendor billing the same amount again under a new invoice number."""
    code = "DUPLICATE_BILLING"
    description = "Same vendor and amount seen earlier (possible double billing)"
    points = 30

    def __init__(self):
        self.seen = set()               # CONCEPT: set remembers what we saw

    def check(self, invoice):
        key = (invoice.gstin, invoice.amount)           # a tuple
        if key in self.seen:
            return True
        self.seen.add(key)
        return False


def build_default_rules():
    """Make a fresh list of rules (the duplicate rule keeps state)."""
    return [NearApprovalLimitRule(), RoundAmountRule(), WeekendInvoiceRule(),
            HighValueRule(), DuplicateBillingRule()]


def risk_level_for(score):
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def score_invoice(invoice, rules):
    """Run every rule on the invoice. Same call works for every rule type
    (polymorphism)."""
    broken = [rule for rule in rules if rule.check(invoice)]
    invoice.flags = [rule.code for rule in broken]
    invoice.risk_score = min(100, sum(rule.points for rule in broken))
    invoice.risk_level = risk_level_for(invoice.risk_score)
    return invoice
