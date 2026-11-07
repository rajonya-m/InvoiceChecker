"""Report generation (CONCEPT: f-strings, Counter, json, writing files)."""
import json
import os
from collections import Counter
from datetime import datetime

from invoiceguard.config import REPORT_DIR
from invoiceguard.rules import build_default_rules


def build_report(db, stats):
    """Return the report as one big string."""
    invoices = db.list_all()
    totals = db.totals()
    by_risk = db.count_by_risk()
    descriptions = {r.code: r.description for r in build_default_rules()}

    # Count how often each flag appears (CONCEPT: Counter from collections)
    flag_counter = Counter(flag for inv in invoices for flag in inv["flags"])

    lines = []
    lines.append("=" * 62)
    lines.append("INVOICEGUARD - VENDOR INVOICE RED-FLAG REPORT")
    lines.append(f"Generated: {datetime.now():%d-%b-%Y %H:%M}")
    lines.append("=" * 62)

    lines.append("\n1. RUN SUMMARY")
    lines.append(f"   Rows read      : {stats['total_rows']}")
    lines.append(f"   Accepted       : {stats['valid']}")
    lines.append(f"   Rejected       : {stats['rejected']}")
    lines.append(f"   Total value    : Rs {totals['total']:,.2f}")

    lines.append("\n2. RISK DISTRIBUTION")
    for level in ["High", "Medium", "Low"]:
        lines.append(f"   {level:<8}: {by_risk.get(level, 0)}")

    lines.append("\n3. TOP RED FLAGS")
    for code, count in flag_counter.most_common():
        lines.append(f"   {code:<18} x{count}  {descriptions[code]}")

    lines.append("\n4. INVOICES NEEDING REVIEW (Medium / High)")
    flagged = [inv for inv in invoices if inv["risk_level"] != "Low"]
    for inv in flagged:
        lines.append(f"   [{inv['risk_level']:<6} {inv['risk_score']:>3}] "
                     f"{inv['invoice_no']}  {inv['vendor_name']}  "
                     f"Rs {inv['amount']:,.2f}")
        lines.append(f"            flags: {', '.join(inv['flags'])}")
    if not flagged:
        lines.append("   None")

    lines.append("\n5. TOP VENDORS BY SPEND")
    for v in db.top_vendors(3):
        lines.append(f"   {v['vendor_name']:<28} {v['invoices']} inv  Rs {v['total']:,.2f}")

    lines.append("\n6. REJECTED ROWS (need correction at source)")
    rejected = db.list_rejected()
    for r in rejected:
        lines.append(f"   line {r['line_no']:>2}: {r['errors']}")
    if not rejected:
        lines.append("   None")

    return "\n".join(lines)


def save_report(db, stats, folder=REPORT_DIR):
    """Write report.txt and flagged_invoices.json. Returns the two file paths."""
    os.makedirs(folder, exist_ok=True)

    text_path = os.path.join(folder, "report.txt")
    with open(text_path, "w", encoding="utf-8") as file:
        file.write(build_report(db, stats))

    flagged = [inv for inv in db.list_all() if inv["risk_level"] != "Low"]
    json_path = os.path.join(folder, "flagged_invoices.json")
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(flagged, file, indent=2)

    return text_path, json_path
