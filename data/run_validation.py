
from collections import Counter
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.migration import run_dry_run
from core.anomaly_detection import detect_invoice_anomalies

from db.session import engine
from db.models import Customer, Vendor, InvoiceStaging
from core.validators import validate_record
from core.scoring import calculate_quality_score, calculate_overall_score
from core.scoring import (
    calculate_quality_score,
    calculate_overall_score,
    save_quality_report
)
from core.migration import (
    run_dry_run,
    save_exceptions,
    migrate_ready_invoices
)

from pathlib import Path


def save_quality_report(entity_scores, overall_score):
    report_folder = Path("reports/generated")
    report_folder.mkdir(parents=True, exist_ok=True)

    report_data = []

    for score in entity_scores:
        report_data.append({
            "entity": score["entity"],
            "total_records": score["total_records"],
            "clean_records": score["clean_records"],
            "affected_records": score["affected_records"],
            "quality_score": score["quality_score"]
        })

    report_data.append({
        "entity": "overall",
        "total_records": sum(
            item["total_records"] for item in entity_scores
        ),
        "clean_records": sum(
            item["clean_records"] for item in entity_scores
        ),
        "affected_records": sum(
            item["affected_records"] for item in entity_scores
        ),
        "quality_score": overall_score
    })

    report = pd.DataFrame(report_data)

    output_path = report_folder / "data_quality_report.csv"
    report.to_csv(output_path, index=False)

    print(f"\nQuality report saved to: {output_path}")



def main():

    with Session(engine) as session:

        # 1. Fetch records from PostgreSQL
        customers = session.scalars(select(Customer)).all()
        vendors = session.scalars(select(Vendor)).all()
        invoices = session.scalars(select(InvoiceStaging)).all()

        print("\nMIGRATIONGUARD 365 - DATA VALIDATION")
        print("=" * 45)
        print(f"Customers loaded: {len(customers)}")
        print(f"Vendors loaded: {len(vendors)}")
        print(f"Invoices loaded: {len(invoices)}")

        customer_csv = pd.read_csv("data/raw/customers.csv")

        customer_dates = dict(
    zip(customer_csv["cust_id"], customer_csv["created_date"])
)

        # 2. Prepare customer records
        customer_records = [
            {
                "name": c.name,
                "tax_id": c.tax_id,
                "email": c.email,
                "phone": c.phone,
                "country": c.country,
                "postal_code": c.postal_code,
                "created_date": customer_dates.get(c.legacy_customer_id),
            }
            for c in customers
        ]

        # 3. Prepare vendor records
        vendor_records = [
            {
                "name": v.name,
                "tax_id": v.tax_id,
                "email": v.email,
                "phone": v.phone,
                "postal_code": v.postal_code,
            }
            for v in vendors
        ]

        # 4. Prepare invoice records
        invoice_records = [
            {
                "invoice_number": i.invoice_number,
                "customer_legacy_id": i.customer_legacy_id,
                "vendor_legacy_id": i.vendor_legacy_id,
                "invoice_date": i.invoice_date_raw,
                "amount": i.amount_raw,
                "currency": i.currency_raw,
                "legacy_invoice_id": i.legacy_invoice_id,
            }
            for i in invoices
        ]

        # 5. Build shared validation context
        context = {
            "customer_ids": {
                c.legacy_customer_id for c in customers
            },
            "vendor_ids": {
                v.legacy_vendor_id for v in vendors
            },
            "vendors": vendor_records,
            "invoices": invoice_records,
            "invoice_ids": [
                i.legacy_invoice_id for i in invoices
            ],
        }

        
       
        all_errors = []
        


        # 6. Validate customers
        
        for customer, record in zip(customers, customer_records):
            errors = validate_record(
                record, "customer", context
            )

            for error in errors:
                all_errors.append({
                    "entity": "customer",
                    "record_id": customer.legacy_customer_id,
                    **error,
                })

        # 7. Validate vendors
        for vendor, record in zip(vendors, vendor_records):
            
            errors = validate_record(
                record, "vendor", context
            )
            

            for error in errors:
                all_errors.append({
                    "entity": "vendor",
                    "record_id": vendor.legacy_vendor_id,
                    **error,
                })

        # 8. Validate invoices
        for invoice, record in zip(invoices, invoice_records):

            invoice_context = context.copy()

            # Build a baseline excluding the current invoice
            vendor_amounts = {}

            for other in invoice_records:
                if (
                    other["vendor_legacy_id"]
                    == record["vendor_legacy_id"]
                    and other["legacy_invoice_id"]
                    != record["legacy_invoice_id"]
                ):
                    try:
                        amount = float(other["amount"])
                        if amount > 0:
                            vendor_amounts.setdefault(
                                other["vendor_legacy_id"], []
                            ).append(amount)
                    except (ValueError, TypeError):
                        pass

            invoice_context["vendor_amounts"] = vendor_amounts

            errors = validate_record(
                record, "invoice", invoice_context
            )

            for error in errors:
                all_errors.append({
                    "entity": "invoice",
                    "record_id": invoice.legacy_invoice_id,
                    **error,
                })

        
        # 8.1 Migration Dry Run

        # Run anomaly detection on invoice records.
        invoice_df = pd.DataFrame(invoice_records)
        anomaly_results = detect_invoice_anomalies(invoice_df)

        anomaly_ids = set(
            anomaly_results.loc[
                anomaly_results["is_anomaly"],
                "legacy_invoice_id"
            ]
        )

        # Prepare record IDs for dry-run classification.
        customer_dry_records = [
            {"record_id": c.legacy_customer_id}
            for c in customers
        ]

        vendor_dry_records = [
            {"record_id": v.legacy_vendor_id}
            for v in vendors
        ]

        invoice_dry_records = [
            {"record_id": i.legacy_invoice_id}
            for i in invoices
        ]

        # Classify each entity.
        customer_dry_results = run_dry_run(
            customer_dry_records, "customer", all_errors
        )

        vendor_dry_results = run_dry_run(
            vendor_dry_records, "vendor", all_errors
        )

        invoice_dry_results = run_dry_run(
            invoice_dry_records,
            "invoice",
            all_errors,
            anomaly_ids
        )

        dry_run_results = (
            customer_dry_results
            + vendor_dry_results
            + invoice_dry_results
        )

                # Save validation and anomaly exceptions
        save_exceptions(
            session,
            all_errors,
            anomaly_ids
        )

        # Execute migration for ready invoices
        migrate_ready_invoices(
            session,
            dry_run_results
        )

        # Display dry-run summary.
        dry_run_counts = Counter(
            result["status"] for result in dry_run_results
        )

        print("\nMIGRATION DRY RUN SUMMARY")
        print("=" * 45)
        print(f"Total records assessed: {len(dry_run_results)}")
        print(f"Ready: {dry_run_counts['ready']}")
        print(f"Needs review: {dry_run_counts['needs_review']}")
        print(f"Rejected: {dry_run_counts['rejected']}")


        # 9. Summarize results
        rule_counts = Counter(
            error["rule_id"] for error in all_errors
        )

        severity_counts = Counter(
            error["severity"] for error in all_errors
        )

        print("\nVALIDATION SUMMARY")
        print("=" * 45)
        print(f"Total records checked: "
              f"{len(customers) + len(vendors) + len(invoices)}")
        print(f"Total validation issues: {len(all_errors)}")

                # 9.1 Data Quality Scoring

        customer_score = calculate_quality_score(
            customers, all_errors, "customer"
        )

        vendor_score = calculate_quality_score(
            vendors, all_errors, "vendor"
        )

        invoice_score = calculate_quality_score(
            invoices, all_errors, "invoice"
        )

        entity_scores = [
            customer_score,
            vendor_score,
            invoice_score
        ]

        overall_score = calculate_overall_score(entity_scores)

        print("\nDATA QUALITY SCORES")
        print("=" * 45)

        for score in entity_scores:
            print(
                f'{score["entity"].upper()}: '
                f'{score["quality_score"]}% '
                f'({score["clean_records"]}/{score["total_records"]} clean)'
            )

        print(f"\nOVERALL DATA QUALITY SCORE: {overall_score}%")

        save_quality_report(entity_scores, overall_score)

        print("\nIssues by rule:")
        for rule_id, count in sorted(rule_counts.items()):
            print(f"{rule_id}: {count}")

        print("\nIssues by severity:")
        for severity, count in severity_counts.items():
            print(f"{severity}: {count}")

        print("\nFirst 15 validation issues:")
        for error in all_errors[:15]:
            print(
                f'{error["entity"].upper()} | '
                f'{error["record_id"]} | '
                f'{error["rule_id"]} | '
                f'{error["message"]}'
            )

        print("\nValidation run completed.")


if __name__ == "__main__":
    main()
