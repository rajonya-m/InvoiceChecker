"""The ETL pipeline: Read -> Validate -> Transform -> Score -> Store."""
from invoiceguard.config import BATCH_SIZE
from invoiceguard.decorators import timed
from invoiceguard.exceptions import FileFormatError, InvoiceValidationError
from invoiceguard.iterators import BatchIterator
from invoiceguard.logger_setup import get_logger
from invoiceguard.readers import read_csv_rows
from invoiceguard.rules import build_default_rules, score_invoice
from invoiceguard.transformer import transform
from invoiceguard.validators import validate_row

log = get_logger()


def process_row(row, rules):
    """validate -> transform -> score for ONE row. Also reused by the REST API."""
    invoice = validate_row(row)
    invoice = transform(invoice)
    return score_invoice(invoice, rules)


@timed
def run_pipeline(csv_path, db):
    """Process a whole CSV file. Returns a dictionary of run statistics."""
    log.info("Pipeline started for %s", csv_path)
    rules = build_default_rules()
    seen_numbers = set()
    good_invoices = []
    stats = {"total_rows": 0, "valid": 0, "rejected": 0}
    db.clear_rejected()

    try:
        for line_no, row in read_csv_rows(csv_path):          # generator
            stats["total_rows"] += 1
            try:
                invoice = process_row(row, rules)
                if invoice.invoice_no in seen_numbers:
                    raise InvoiceValidationError(
                        [f"duplicate invoice number {invoice.invoice_no}"])
                seen_numbers.add(invoice.invoice_no)
                good_invoices.append(invoice)
                stats["valid"] += 1
            except InvoiceValidationError as error:
                stats["rejected"] += 1
                db.save_rejected(line_no, row, error.errors)
                log.warning("Line %d rejected: %s", line_no, error)

    except FileNotFoundError:
        log.error("File not found: %s", csv_path)
        raise
    except FileFormatError as error:
        log.error("Bad file format: %s", error)
        raise

    for batch in BatchIterator(good_invoices, BATCH_SIZE):    # custom iterator
        db.save_many(batch)
        log.info("Saved a batch of %d invoice(s)", len(batch))

    log.info("Pipeline finished: %s", stats)
    return stats
