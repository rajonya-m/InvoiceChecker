"""REST API on top of the same database (CONCEPT: REST, HTTP methods, CRUD).

Run:  uvicorn invoiceguard.api:app --reload      then open /docs
"""
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

from invoiceguard.database import InvoiceDB
from invoiceguard.exceptions import InvoiceExistsError, InvoiceValidationError
from invoiceguard.pipeline import process_row
from invoiceguard.rules import build_default_rules

app = FastAPI(title="InvoiceGuard API", version="1.0")
db = InvoiceDB()


class InvoiceIn(BaseModel):
    invoice_no: str
    vendor_name: str
    gstin: str
    invoice_date: str            # YYYY-MM-DD
    amount: float
    email: str
    description: str = ""


def build_invoice(body):
    """Reuse the SAME validation + scoring the pipeline uses."""
    row = {key: str(value) for key, value in body.model_dump().items()}
    try:
        return process_row(row, build_default_rules())
    except InvoiceValidationError as error:
        raise HTTPException(422, detail=error.errors)


@app.get("/invoices")
def list_invoices(risk_level: Optional[str] = None):
    return db.list_all(risk_level)


@app.get("/invoices/{invoice_no}")
def get_invoice(invoice_no: str):
    invoice = db.get(invoice_no)
    if invoice is None:
        raise HTTPException(404, "Invoice not found")
    return invoice


@app.post("/invoices", status_code=201)
def create_invoice(body: InvoiceIn):
    invoice = build_invoice(body)
    try:
        db.create(invoice)
    except InvoiceExistsError as error:
        raise HTTPException(409, str(error))
    return invoice.to_dict()


@app.put("/invoices/{invoice_no}")
def replace_invoice(invoice_no: str, body: InvoiceIn):
    if body.invoice_no != invoice_no:
        raise HTTPException(400, "invoice_no in body must match the URL")
    invoice = build_invoice(body)
    if not db.update(invoice):
        raise HTTPException(404, "Invoice not found")
    return invoice.to_dict()


@app.delete("/invoices/{invoice_no}", status_code=204)
def delete_invoice(invoice_no: str):
    if not db.delete(invoice_no):
        raise HTTPException(404, "Invoice not found")
    return Response(status_code=204)


@app.get("/summary")
def summary():
    return {"totals": db.totals(), "by_risk_level": db.count_by_risk(),
            "top_vendors": db.top_vendors(3)}
