"""SQLite storage (CONCEPT: SQL, database connectivity, CRUD, GROUP BY)."""
import sqlite3
from datetime import datetime

from invoiceguard.config import DB_PATH
from invoiceguard.decorators import retry
from invoiceguard.exceptions import InvoiceExistsError
from invoiceguard.logger_setup import get_logger

log = get_logger()

CREATE_INVOICES = """
CREATE TABLE IF NOT EXISTS invoices (
    invoice_no   TEXT PRIMARY KEY,
    vendor_name  TEXT NOT NULL,
    gstin        TEXT NOT NULL,
    state        TEXT,
    invoice_date TEXT NOT NULL,
    amount       REAL NOT NULL,
    email        TEXT,
    description  TEXT,
    flags        TEXT,
    risk_score   INTEGER,
    risk_level   TEXT
)"""

CREATE_REJECTED = """
CREATE TABLE IF NOT EXISTS rejected_rows (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    line_no   INTEGER,
    raw_data  TEXT,
    errors    TEXT,
    run_at    TEXT
)"""


def _to_tuple(inv):
    """Invoice object -> tuple of values in column order."""
    return (inv.invoice_no, inv.vendor_name, inv.gstin, inv.state,
            inv.invoice_date.isoformat(), inv.amount, inv.email,
            inv.description, ",".join(inv.flags), inv.risk_score, inv.risk_level)


def _to_dict(row):
    """sqlite row -> dictionary (flags turned back into a list)."""
    data = dict(row)
    data["flags"] = data["flags"].split(",") if data["flags"] else []
    return data


class InvoiceDB:
    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row         # lets us read columns by name
        self.conn.execute(CREATE_INVOICES)
        self.conn.execute(CREATE_REJECTED)
        self.conn.commit()

    # allows:  with InvoiceDB() as db:  ...   (connection closes automatically)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.close()

    # ------------------------------------------------------------ CREATE
    def create(self, inv):
        """Insert ONE new invoice. Refuses if the number already exists."""
        if self.get(inv.invoice_no) is not None:
            raise InvoiceExistsError(f"{inv.invoice_no} already exists")
        self.conn.execute("INSERT INTO invoices VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                          _to_tuple(inv))
        self.conn.commit()

    @retry(times=3, exceptions=(sqlite3.OperationalError,))
    def save_many(self, invoices):
        """Insert a batch; replaces rows that already exist (used by pipeline)."""
        self.conn.executemany(
            "INSERT OR REPLACE INTO invoices VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [_to_tuple(inv) for inv in invoices])
        self.conn.commit()

    def save_rejected(self, line_no, raw_row, errors):
        self.conn.execute(
            "INSERT INTO rejected_rows (line_no, raw_data, errors, run_at) VALUES (?,?,?,?)",
            (line_no, str(dict(raw_row)), "; ".join(errors),
             datetime.now().isoformat(timespec="seconds")))
        self.conn.commit()

    def clear_rejected(self):
        self.conn.execute("DELETE FROM rejected_rows")
        self.conn.commit()

    # ------------------------------------------------------------ READ
    def get(self, invoice_no):
        row = self.conn.execute("SELECT * FROM invoices WHERE invoice_no = ?",
                                (invoice_no,)).fetchone()
        return _to_dict(row) if row else None

    def list_all(self, risk_level=None):
        sql = "SELECT * FROM invoices"
        params = ()
        if risk_level:
            sql += " WHERE risk_level = ?"
            params = (risk_level,)
        sql += " ORDER BY risk_score DESC, invoice_no"
        return [_to_dict(r) for r in self.conn.execute(sql, params)]

    def list_rejected(self):
        rows = self.conn.execute("SELECT * FROM rejected_rows ORDER BY line_no")
        return [dict(r) for r in rows]

    # ------------------------------------------------------------ UPDATE
    def update(self, inv):
        """Overwrite an existing invoice. Returns False if it doesn't exist."""
        cursor = self.conn.execute(
            """UPDATE invoices SET vendor_name=?, gstin=?, state=?, invoice_date=?,
               amount=?, email=?, description=?, flags=?, risk_score=?, risk_level=?
               WHERE invoice_no=?""",
            _to_tuple(inv)[1:] + (inv.invoice_no,))
        self.conn.commit()
        return cursor.rowcount > 0

    # ------------------------------------------------------------ DELETE
    def delete(self, invoice_no):
        cursor = self.conn.execute("DELETE FROM invoices WHERE invoice_no = ?",
                                   (invoice_no,))
        self.conn.commit()
        return cursor.rowcount > 0

    # ------------------------------------------------------------ analytics (SQL)
    def count_by_risk(self):
        sql = "SELECT risk_level, COUNT(*) AS n FROM invoices GROUP BY risk_level"
        return {r["risk_level"]: r["n"] for r in self.conn.execute(sql)}

    def top_vendors(self, limit=3):
        sql = """SELECT vendor_name, COUNT(*) AS invoices, SUM(amount) AS total
                 FROM invoices GROUP BY vendor_name
                 ORDER BY total DESC LIMIT ?"""
        return [dict(r) for r in self.conn.execute(sql, (limit,))]

    def totals(self):
        sql = "SELECT COUNT(*) AS n, COALESCE(SUM(amount),0) AS total FROM invoices"
        return dict(self.conn.execute(sql).fetchone())
