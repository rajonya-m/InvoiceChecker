import pytest

from invoiceguard.database import InvoiceDB
from invoiceguard.exceptions import FileFormatError
from invoiceguard.pipeline import run_pipeline
from invoiceguard.report import build_report, save_report

HEADER = "invoice_no,vendor_name,gstin,invoice_date,amount,email,description\n"
GOOD = "INV-2026-001,acme traders,19ABCDE1234F1Z5,2026-10-05,1000.50,a@b.com,x\n"
BAD = "INV-2026-002,acme,BADGSTIN,2026-10-05,10,a@b.com,x\n"
DUP = "INV-2026-001,acme traders,19ABCDE1234F1Z5,2026-10-06,2000,a@b.com,x\n"


@pytest.fixture
def db():
    database = InvoiceDB(":memory:")
    yield database
    database.conn.close()


def write_csv(tmp_path, text):
    path = tmp_path / "in.csv"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_good_and_bad_rows_are_split(tmp_path, db):
    stats = run_pipeline(write_csv(tmp_path, HEADER + GOOD + BAD + DUP), db)
    assert stats == {"total_rows": 3, "valid": 1, "rejected": 2}
    assert db.get("INV-2026-001")["vendor_name"] == "Acme Traders"      # transformed
    assert db.get("INV-2026-001")["state"] == "West Bengal"
    assert len(db.list_rejected()) == 2


def test_missing_file_raises(db):
    with pytest.raises(FileNotFoundError):
        run_pipeline("does_not_exist.csv", db)


def test_missing_columns_raises(tmp_path, db):
    with pytest.raises(FileFormatError):
        run_pipeline(write_csv(tmp_path, "a,b\n1,2\n"), db)


def test_rerun_does_not_duplicate(tmp_path, db):
    path = write_csv(tmp_path, HEADER + GOOD)
    run_pipeline(path, db)
    run_pipeline(path, db)
    assert db.totals()["n"] == 1


def test_report_files(tmp_path, db):
    stats = run_pipeline(write_csv(tmp_path, HEADER + GOOD + BAD), db)
    assert "RED-FLAG REPORT" in build_report(db, stats)
    text_path, json_path = save_report(db, stats, folder=str(tmp_path / "out"))
    assert open(text_path, encoding="utf-8").read().startswith("=")
    assert json_path.endswith(".json")
