# InvoiceGuard - Vendor Invoice Red-Flag Detector

Reads vendor invoices from a CSV, **validates** them, **transforms** them, scores them
against audit **red-flag rules**, **stores** the results in SQLite, and **generates a report**.
Bad rows are never lost: they are rejected with clear reasons and saved for correction.

## Run
```bash
pip install -r requirements.txt
python main.py data/invoices.csv        # runs the pipeline, prints + saves the report
pytest -q                               # 27 unit tests
uvicorn invoiceguard.api:app --reload   # REST API, docs at http://127.0.0.1:8000/docs
```
Outputs: `reports/report.txt`, `reports/flagged_invoices.json`, `invoiceguard.db`, `logs/invoiceguard.log`

## Flow
```
invoices.csv -> read (generator) -> validate (regex) -> transform -> score (rules)
             -> store in SQLite (batches) -> report (txt + json)
                    \-> rejected rows (with reasons) -> rejected_rows table + log
```

## Red-flag rules
| Code | Meaning | Points |
|---|---|---|
| NEAR_LIMIT | Amount 5% below the Rs 50,000 approval limit (invoice splitting) | 25 |
| ROUND_AMOUNT | Round figure of Rs 10,000+ (e.g. 80,000) | 10 |
| WEEKEND | Invoice dated Sat/Sun | 15 |
| HIGH_VALUE | Rs 2,00,000 or more | 25 |
| DUPLICATE_BILLING | Same vendor + same amount seen before, new invoice number | 30 |

Risk level: 50+ High, 25-49 Medium, below 25 Low.

## Where each topic from your syllabus appears
| Topic | File |
|---|---|
| Variables, control flow, loops | `validators.py`, `pipeline.py`, `report.py` |
| Collections (list, dict, set, tuple, Counter) | `config.py` (dict), `rules.py` (set + tuple), `report.py` (Counter) |
| Functions & modular programming | whole `invoiceguard/` package (one job per file) |
| File handling & data formats (CSV, JSON, TXT) | `readers.py`, `report.py` |
| Exceptions (try/except, custom) | `exceptions.py`, `pipeline.py` |
| Regex | `validators.py` (GSTIN, invoice no, email) |
| OOP (classes, inheritance, polymorphism, dunder methods) | `models.py`, `rules.py`, `database.py` |
| Generators | `readers.py` (`yield`) + generator expression in `report.py` |
| Iterators | `iterators.py` (`__iter__` / `__next__`) |
| Decorators (plain and with arguments) | `decorators.py` (`@timed`, `@retry(times=3)`) |
| Logging | `logger_setup.py` -> `logs/invoiceguard.log` |
| SQL (CREATE, INSERT, SELECT, UPDATE, DELETE, GROUP BY) | `database.py` |
| Database connectivity & CRUD | `database.py` (sqlite3) |
| REST API (GET, POST, PUT, DELETE) | `api.py` |
| Unit tests | `tests/` |
