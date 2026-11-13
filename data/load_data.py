import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.session import engine
from db.models import Customer, Vendor, InvoiceStaging

def load_customers(session):
    customers_df = pd.read_csv("data/raw/customers.csv")

    inserted = 0
    skipped = 0

    for _, row in customers_df.iterrows():
        existing_customer = session.scalar(
            select(Customer).where(
                Customer.legacy_customer_id == row["cust_id"]
            )
        )

        if existing_customer:
            skipped += 1
            continue

        customer = Customer(
            legacy_customer_id=row["cust_id"],
            name=row["cust_nm"],
            email=row["email"],
            tax_id=None if pd.isna(row["tax_no"]) else str(row["tax_no"]),
            phone=row["phone"],
            country=row["country"],
            postal_code=row["postal_code"]
        )

        session.add(customer)
        inserted += 1

    session.commit()
    print(f"Customers: {inserted} inserted, {skipped} skipped.")

    
def load_vendors(session):
    vendors_df = pd.read_csv("data/raw/vendors.csv")

    inserted = 0
    skipped = 0

    for _, row in vendors_df.iterrows():
        existing_vendor = session.scalar(
            select(Vendor).where(
                Vendor.legacy_vendor_id == row["vendor_id"]
            )
        )

        if existing_vendor:
            skipped += 1
            continue


        vendor = Vendor(
            legacy_vendor_id=row["vendor_id"],
            name=row["vendor_nm"],
            email=row["email"],
            tax_id=row["tax_no"],
            phone=row["phone"],
            country=row["country"],
            postal_code=row["postal_code"]
        )

        session.add(vendor)
        inserted += 1

    session.commit()

    print(f"Vendors: {inserted} inserted, {skipped} skipped.")

    

def load_invoices(session):
    invoices_df = pd.read_csv("data/raw/invoices.csv")

    inserted = 0
    skipped = 0

    for _, row in invoices_df.iterrows():
        existing_invoice = session.scalar(
            select(InvoiceStaging).where(
                InvoiceStaging.legacy_invoice_id == row["inv_id"]
            )
        )

        if existing_invoice:
            skipped += 1
            continue

        invoice = InvoiceStaging(
            legacy_invoice_id=row["inv_id"],
            invoice_number=row["inv_no"],
            customer_legacy_id=row["cust_id"],
            vendor_legacy_id=row["vendor_id"],
            invoice_date_raw=str(row["inv_dt"]),
            amount_raw=str(row["inv_amt"]),
            currency_raw=row["currency"]
        )

        session.add(invoice)
        inserted += 1

    session.commit()
    print(f"Invoices: {inserted} inserted, {skipped} skipped.")

def main():
    with Session(engine) as session:
        load_customers(session)
        load_vendors(session)
        load_invoices(session)

    print("ERP data ingestion completed!")


if __name__ == "__main__":
    main()