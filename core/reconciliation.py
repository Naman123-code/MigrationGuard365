from sqlalchemy.orm import Session
from db.models import InvoiceStaging, Invoice
import pandas as pd

def reconcile_counts(session: Session):

    source_count = session.query(InvoiceStaging).count()
    target_count = session.query(Invoice).count()

    missing_count = source_count - target_count

    return {
        "source_count": source_count,
        "target_count": target_count,
        "missing_count": missing_count
    }

def find_missing_invoices(session: Session):

    source_ids = {
        row[0]
        for row in session.query(
            InvoiceStaging.legacy_invoice_id
        ).all()
    }

    target_ids = {
        row[0]
        for row in session.query(
            Invoice.legacy_invoice_id
        ).all()
    }

    missing_ids = source_ids - target_ids

    return sorted(missing_ids)

from datetime import datetime
from decimal import Decimal


def compare_invoice_data(session: Session):

    mismatches = []

    staging_records = session.query(InvoiceStaging).all()

    for source in staging_records:

        target = session.query(Invoice).filter_by(
            legacy_invoice_id=source.legacy_invoice_id
        ).first()

        # Skip invoices that were not migrated
        if not target:
            continue

        source_amount = Decimal(source.amount_raw)
        source_date = datetime.strptime(
            source.invoice_date_raw, "%d/%m/%Y"
        ).date()

        if (
            source_amount != target.amount
            or source_date != target.invoice_date
            or source.currency_raw != target.currency
        ):
            mismatches.append(source.legacy_invoice_id)

    return mismatches

def run_reconciliation(session: Session):

    counts = reconcile_counts(session)
    missing = find_missing_invoices(session)
    mismatches = compare_invoice_data(session)

    results = {
        **counts,
        "missing_invoices": missing,
        "mismatched_invoices": mismatches
    }

    print("\nRECONCILIATION SUMMARY")
    print("=" * 40)

    print(f"Source invoices: {counts['source_count']}")
    print(f"Target invoices: {counts['target_count']}")
    print(f"Missing invoices: {len(missing)}")
    print(f"Mismatched invoices: {len(mismatches)}")

    save_reconciliation_report(results)

    return results

def save_reconciliation_report(results):

    report_data = [
        {"Metric": "Source Invoices", "Value": results["source_count"]},
        {"Metric": "Target Invoices", "Value": results["target_count"]},
        {"Metric": "Missing Invoices", "Value": len(results["missing_invoices"])},
        {"Metric": "Mismatched Invoices", "Value": len(results["mismatched_invoices"])}
    ]

    report_df = pd.DataFrame(report_data)

    report_df.to_csv(
        "reports/generated/reconciliation_report.csv",
        index=False
    )

    print("\nReconciliation report saved successfully!")