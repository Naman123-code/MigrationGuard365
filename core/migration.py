from datetime import datetime
from sqlalchemy.orm import Session
from db.models import MigrationException, Customer, Vendor, Invoice
from sqlalchemy import select
from decimal import Decimal
from db.models import InvoiceStaging


def classify_record(record_id, entity, errors, anomaly_ids=None):
    """
    Classify a record using its validation errors
    and optional anomaly detection result.
    """

    anomaly_ids = anomaly_ids or set()

    record_errors = [
        error for error in errors
        if error["entity"] == entity
        and error["record_id"] == record_id
    ]

    # Any reject action takes priority.
    if any(error["action"] == "reject" for error in record_errors):
        status = "rejected"

    # Validation issues or anomaly flags require review.
    elif record_errors or record_id in anomaly_ids:
        status = "needs_review"

    else:
        status = "ready"

    return {
        "record_id": record_id,
        "entity": entity,
        "status": status,
        "issue_count": len(record_errors)
    }


def run_dry_run(records, entity, errors, anomaly_ids=None):
    """
    Classify all records without migrating them.
    """

    results = []

    for record in records:
        result = classify_record(
            record_id=record["record_id"],
            entity=entity,
            errors=errors,
            anomaly_ids=anomaly_ids
        )

        results.append(result)

    return results


def save_exceptions(session, validation_errors, anomaly_ids=None):
    anomaly_ids = anomaly_ids or set()

    existing_keys = set(
        session.execute(
            select(
                MigrationException.entity,
                MigrationException.record_id,
                MigrationException.rule_id
            )
        ).all()
    )

    added = 0

    # Save validation exceptions
    for error in validation_errors:
        key = (
            error["entity"],
            error["record_id"],
            error["rule_id"]
        )

        if key in existing_keys:
            continue

        session.add(
            MigrationException(
                entity=error["entity"],
                record_id=error["record_id"],
                rule_id=error["rule_id"],
                description=error["message"],
                status="pending"
            )
        )

        existing_keys.add(key)
        added += 1

    # Save anomaly exceptions
    for invoice_id in anomaly_ids:
        key = ("invoice", invoice_id, "ANOMALY")

        if key in existing_keys:
            continue

        session.add(
            MigrationException(
                entity="invoice",
                record_id=invoice_id,
                rule_id="ANOMALY",
                description="Unusual invoice amount detected by Isolation Forest",
                status="pending"
            )
        )

        existing_keys.add(key)
        added += 1

    session.commit()

    print(f"New exceptions saved: {added}")

def resolve_exception(session, exception_id, corrected_value):

    exception = session.get(MigrationException, exception_id)

    if not exception:
        raise ValueError("Exception not found")

    if exception.status == "resolved":
        raise ValueError("Exception is already resolved")

    if exception.entity == "customer":
        record = session.query(Customer).filter_by(
            legacy_customer_id=exception.record_id
        ).first()

    elif exception.entity == "vendor":
        record = session.query(Vendor).filter_by(
            legacy_vendor_id=exception.record_id
        ).first()

    elif exception.entity == "invoice":
        record = session.query(Invoice).filter_by(
            legacy_invoice_id=exception.record_id
        ).first()

    else:
        raise ValueError("Unsupported entity")

    if not record:
        raise ValueError("Source record not found")

    field_mapping = {
        "V03": "email",
        "V05": "country",
        "V08": "phone",
        "V11": "amount",
        "V12": "currency"
    }

    field = field_mapping.get(exception.rule_id)

    if not field:
        raise ValueError("Correction for this rule is not supported yet")

    exception.original_value = str(getattr(record, field))
    setattr(record, field, corrected_value)

    exception.corrected_value = str(corrected_value)
    exception.status = "resolved"
    exception.resolved_at = datetime.utcnow()

    session.commit()

    return True

def migrate_ready_invoices(session: Session, dry_run_results):

    migrated = 0
    skipped = 0

    # Get invoice IDs classified as ready
    ready_invoice_ids = {
        result["record_id"]
        for result in dry_run_results
        if result["entity"] == "invoice"
        and result["status"] == "ready"
    }

    for invoice_id in ready_invoice_ids:

        # Avoid duplicate migration
        existing = session.query(Invoice).filter_by(
            legacy_invoice_id=invoice_id
        ).first()

        if existing:
            skipped += 1
            continue

        # Get original staging record
        staging = session.query(InvoiceStaging).filter_by(
            legacy_invoice_id=invoice_id
        ).first()

        if not staging:
            skipped += 1
            continue

        # Find matching customer
        customer = session.query(Customer).filter_by(
            legacy_customer_id=staging.customer_legacy_id
        ).first()

        # Find matching vendor
        vendor = session.query(Vendor).filter_by(
            legacy_vendor_id=staging.vendor_legacy_id
        ).first()

        if not customer or not vendor:
            skipped += 1
            continue

        try:
            invoice_date = datetime.strptime(
                staging.invoice_date_raw, "%d/%m/%Y"
            ).date()

            amount = Decimal(staging.amount_raw)

        except (ValueError, TypeError):
            skipped += 1
            continue

        # Create target invoice
        new_invoice = Invoice(
            legacy_invoice_id=staging.legacy_invoice_id,
            invoice_number=staging.invoice_number,
            customer_id=customer.id,
            vendor_id=vendor.id,
            invoice_date=invoice_date,
            amount=amount,
            currency=staging.currency_raw
        )

        session.add(new_invoice)
        migrated += 1

    session.commit()

    print("\nMIGRATION EXECUTION SUMMARY")
    print("=" * 40)
    print(f"Successfully migrated: {migrated}")
    print(f"Skipped: {skipped}")

    return migrated, skipped

