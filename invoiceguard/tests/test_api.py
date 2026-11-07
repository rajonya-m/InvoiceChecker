import pytest
from fastapi.testclient import TestClient

from invoiceguard import api
from invoiceguard.database import InvoiceDB

BODY = {"invoice_no": "INV-2026-100", "vendor_name": "acme traders",
        "gstin": "19ABCDE1234F1Z5", "invoice_date": "2026-10-05",
        "amount": 49500, "email": "a@b.com", "description": "test"}


@pytest.fixture
def client():
    api.db = InvoiceDB(":memory:")          # each test gets a clean database
    return TestClient(api.app)


def test_full_crud_cycle(client):
    r = client.post("/invoices", json=BODY)
    assert r.status_code == 201 and r.json()["flags"] == ["NEAR_LIMIT"]
    assert client.post("/invoices", json=BODY).status_code == 409        # duplicate

    assert client.get("/invoices/INV-2026-100").json()["vendor_name"] == "Acme Traders"
    assert len(client.get("/invoices?risk_level=Medium").json()) == 1

    changed = dict(BODY, amount=1234.5)
    r = client.put("/invoices/INV-2026-100", json=changed)
    assert r.status_code == 200 and r.json()["flags"] == []              # re-scored

    assert client.get("/summary").json()["totals"]["n"] == 1
    assert client.delete("/invoices/INV-2026-100").status_code == 204
    assert client.get("/invoices/INV-2026-100").status_code == 404


def test_validation_error_returns_422(client):
    r = client.post("/invoices", json=dict(BODY, gstin="bad"))
    assert r.status_code == 422


def test_put_mismatch_and_missing(client):
    assert client.put("/invoices/INV-2026-999", json=BODY).status_code == 400
    assert client.put("/invoices/INV-2026-100", json=BODY).status_code == 404
