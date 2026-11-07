"""Settings kept in one place (CONCEPT: constants, modular programming)."""

APPROVAL_LIMIT = 50000          # invoices above this need senior approval
NEAR_LIMIT_BAND = 0.05          # "near the limit" = within 5% below it
HIGH_VALUE_LIMIT = 200000
ROUND_AMOUNT_MIN = 10000

DB_PATH = "invoiceguard.db"
LOG_FILE = "logs/invoiceguard.log"
REPORT_DIR = "reports"
BATCH_SIZE = 5                  # how many invoices we save to the DB at a time

REQUIRED_COLUMNS = ["invoice_no", "vendor_name", "gstin",
                    "invoice_date", "amount", "email", "description"]

# First two digits of a GSTIN tell us the state (CONCEPT: dictionary lookup)
STATE_CODES = {
    "07": "Delhi", "19": "West Bengal", "27": "Maharashtra",
    "29": "Karnataka", "33": "Tamil Nadu",
}
