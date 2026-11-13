
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.session import engine
from db.models import InvoiceStaging
from core.anomaly_detection import detect_invoice_anomalies


def main():
    with Session(engine) as session:

        invoices = session.scalars(
            select(InvoiceStaging)
        ).all()

        invoice_data = [
            {
                "legacy_invoice_id": invoice.legacy_invoice_id,
                "invoice_number": invoice.invoice_number,
                "vendor_legacy_id": invoice.vendor_legacy_id,
                "amount": invoice.amount_raw
            }
            for invoice in invoices
        ]

    df = pd.DataFrame(invoice_data)

    results = detect_invoice_anomalies(df)

    anomalies = results[results["is_anomaly"]]

    print(f"Total invoices analysed: {len(results)}")
    print(f"Anomalies detected: {len(anomalies)}")

    print("\nFirst 10 unusual invoices:")
    print(
        anomalies[
            ["legacy_invoice_id", "invoice_number", "amount", "anomaly_score"]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()
