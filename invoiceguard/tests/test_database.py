import pytest

from invoiceguard.database import InvoiceDB
from invoiceguard.exceptions import InvoiceExistsError
from invoiceguard.models import Invoice
from datetime import date


def make(no="INV-2026-001", amount=100.0, level="Low"):
    return Invoice(no, "Acme", "19ABCDE1234F1Z5", date(2026, 10, 5), amount,
                   "a@b.com", "d", "West Bengal", ["WEEKEND"], 15, level)


@pytest.fixture
def db():
    database = InvoiceDB(":memory:")         # throw-away database for each test
    yield database
    database.conn.close()


def test_create_and_get(db):
    db.create(make())
    row = db.get("INV-2026-001")
    assert row["vendor_name"] == "Acme" and row["flags"] == ["WEEKEND"]


def test_create_duplicate_fails(db):
    db.create(make())
    with pytest.raises(InvoiceExistsError):
        db.create(make())


def test_update_and_delete(db):
    db.create(make())
    assert db.update(make(amount=999.0)) is True
    assert db.get("INV-2026-001")["amount"] == 999.0
    assert db.delete("INV-2026-001") is True
    assert db.get("INV-2026-001") is None
    assert db.delete("INV-2026-001") is False
    assert db.update(make()) is False


def test_group_by_queries(db):
    db.save_many([make("INV-2026-001", 100, "Low"), make("INV-2026-002", 300, "High"),
                  make("INV-2026-003", 200, "High")])
    assert db.count_by_risk() == {"Low": 1, "High": 2}
    assert db.top_vendors(1)[0]["total"] == 600.0
    assert [i["invoice_no"] for i in db.list_all("High")] == ["INV-2026-002", "INV-2026-003"]
