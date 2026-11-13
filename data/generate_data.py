import random
import json
from pathlib import Path
from faker import Faker
import pandas as pd

fake = Faker()

# Fixed seeds ensure the same data is generated every time.
Faker.seed(42)
random.seed(42)

# Number of records to generate
CUSTOMER_COUNT = 1000
VENDOR_COUNT = 300
INVOICE_COUNT = 3000

def generate_customers():
    customers = []

    for i in range(1, CUSTOMER_COUNT + 1):
        customer = {
            "cust_id": f"CUST{i:04d}",
            "cust_nm": fake.name(),
            "email": fake.email(),
            "tax_no": f"GST{random.randint(1000000000, 9999999999)}",
            "phone": fake.phone_number(),
            "country": "IN",
            "postal_code": fake.postcode(),
            "created_date": fake.date_between(
                start_date="-5y",
                end_date="today"
            ).isoformat()
        }

        customers.append(customer)

    return pd.DataFrame(customers)


def generate_vendors():
    vendors = []

    for i in range(1, VENDOR_COUNT + 1):
        vendor = {
            "vendor_id": f"VEND{i:04d}",
            "vendor_nm": fake.company(),
            "email": fake.company_email(),
            "tax_no": f"GST{random.randint(1000000000, 9999999999)}",
            "phone": fake.phone_number(),
            "country": "IN",
            "postal_code": fake.postcode()
        }

        vendors.append(vendor)

    return pd.DataFrame(vendors)

def generate_invoices(customers, vendors):
    invoices = []

    for i in range(1, INVOICE_COUNT + 1):
        invoice = {
            "inv_id": f"INV{i:05d}",
            "inv_no": f"INV-{random.randint(10000, 99999)}",
            "cust_id": random.choice(customers["cust_id"].tolist()),
            "vendor_id": random.choice(vendors["vendor_id"].tolist()),
            "inv_dt": fake.date_between(
                start_date="-2y",
                end_date="today"
            ).strftime("%d/%m/%Y"),
            "inv_amt": round(random.uniform(500, 100000), 2),
            "currency": random.choice(["INR", "USD", "EUR"])
        }

        invoices.append(invoice)

    return pd.DataFrame(invoices)


BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("Generating synthetic ERP data...")

    customers = generate_customers()
    vendors = generate_vendors()
    invoices = generate_invoices(customers, vendors)

    print("Customer records:", len(customers))
    print("Vendor records:", len(vendors))
    print("Invoice records:", len(invoices))

    

    injected_errors = {
        "customers": [],
        "vendors": [],
        "invoices": []
    }

        # Inject 15 missing customer tax IDs
    missing_tax_ids = random.sample(range(len(customers)), 15)

    for index in missing_tax_ids:
        customers.loc[index, "tax_no"] = None

        injected_errors["customers"].append({
            "record_id": customers.loc[index, "cust_id"],
            "field": "tax_no",
            "error": "missing_tax_id"
        })

        # Inject 10 invalid customer emails
    invalid_emails = random.sample(range(len(customers)), 10)

    for index in invalid_emails:
        customers.loc[index, "email"] = "invalid-email"

        injected_errors["customers"].append({
            "record_id": customers.loc[index, "cust_id"],
            "field": "email",
            "error": "invalid_email"
        })

        # Inject 10 invalid customer creation dates
    invalid_dates = random.sample(range(len(customers)), 10)

    for index in invalid_dates:
        customers.loc[index, "created_date"] = "not-a-date"

        injected_errors["customers"].append({
            "record_id": customers.loc[index, "cust_id"],
            "field": "created_date",
            "error": "invalid_date"
        })

        # Inject 5 invalid customer country codes
    invalid_countries = random.sample(range(len(customers)), 5)

    for index in invalid_countries:
        customers.loc[index, "country"] = "XX"

        injected_errors["customers"].append({
            "record_id": customers.loc[index, "cust_id"],
            "field": "country",
            "error": "invalid_country"
        })

        # Inject 8 duplicate vendors
    duplicate_vendors = random.sample(range(8, len(vendors)), 8)

    for index in duplicate_vendors:
        vendors.loc[index, "vendor_nm"] = vendors.loc[index - 1, "vendor_nm"]
        vendors.loc[index, "tax_no"] = vendors.loc[index - 1, "tax_no"]
        vendors.loc[index, "postal_code"] = vendors.loc[index - 1, "postal_code"]

        injected_errors["vendors"].append({
            "record_id": vendors.loc[index, "vendor_id"],
            "field": "vendor_nm",
            "error": "duplicate_vendor"
        })

        # Inject 6 missing vendor tax IDs
    missing_vendor_tax_ids = random.sample(range(len(vendors)), 6)

    for index in missing_vendor_tax_ids:
        vendors.loc[index, "tax_no"] = None

        injected_errors["vendors"].append({
            "record_id": vendors.loc[index, "vendor_id"],
            "field": "tax_no",
            "error": "missing_tax_id"
        })

        # Inject 4 invalid vendor phone numbers
    invalid_vendor_phones = random.sample(range(len(vendors)), 4)

    for index in invalid_vendor_phones:
        vendors.loc[index, "phone"] = "ABC123"

        injected_errors["vendors"].append({
            "record_id": vendors.loc[index, "vendor_id"],
            "field": "phone",
            "error": "invalid_phone"
        })
 
        # Inject 10 invoices with nonexistent customer IDs
    orphan_invoices = random.sample(range(len(invoices)), 10)

    for index in orphan_invoices:
        invoices.loc[index, "cust_id"] = "CUST99999"

        injected_errors["invoices"].append({
            "record_id": invoices.loc[index, "inv_id"],
            "field": "cust_id",
            "error": "orphan_customer_reference"
        })

        # Inject 10 duplicate invoices
    duplicate_invoices = random.sample(range(1, len(invoices)), 10)

    for index in duplicate_invoices:
        invoices.loc[index, "inv_no"] = invoices.loc[index - 1, "inv_no"]
        invoices.loc[index, "vendor_id"] = invoices.loc[index - 1, "vendor_id"]
        invoices.loc[index, "inv_amt"] = invoices.loc[index - 1, "inv_amt"]

        injected_errors["invoices"].append({
            "record_id": invoices.loc[index, "inv_id"],
            "field": "inv_no",
            "error": "duplicate_invoice"
        })

        # Inject 8 invalid invoice amounts
    invalid_amounts = random.sample(range(len(invoices)), 8)

    for index in invalid_amounts:
        invoices.loc[index, "inv_amt"] = -500

        injected_errors["invoices"].append({
            "record_id": invoices.loc[index, "inv_id"],
            "field": "inv_amt",
            "error": "negative_invoice_amount"
        })
          
    # Inject 5 invoices with future dates
    future_dates = random.sample(range(len(invoices)), 5)

    for index in future_dates:
        invoices.loc[index, "inv_dt"] = "31/12/2030"

        injected_errors["invoices"].append({
            "record_id": invoices.loc[index, "inv_id"],
            "field": "inv_dt",
            "error": "future_invoice_date"
        })

        # Inject 5 invalid invoice currencies
    invalid_currencies = random.sample(range(len(invoices)), 5)

    for index in invalid_currencies:
        invoices.loc[index, "currency"] = "XYZ"

        injected_errors["invoices"].append({
            "record_id": invoices.loc[index, "inv_id"],
            "field": "currency",
            "error": "invalid_currency"
        })

        # Inject 6 unusually large invoice amounts
    outlier_amounts = random.sample(range(len(invoices)), 6)

    for index in outlier_amounts:
        invoices.loc[index, "inv_amt"] = 10000000

        injected_errors["invoices"].append({
            "record_id": invoices.loc[index, "inv_id"],
            "field": "inv_amt",
            "error": "extreme_invoice_amount"
        })

    customers.to_csv(RAW_DIR / "customers.csv", index=False)
    vendors.to_csv(RAW_DIR / "vendors.csv", index=False)
    invoices.to_csv(RAW_DIR / "invoices.csv", index=False)

        # Save injected error manifest
    error_file = BASE_DIR / "injected_errors.json"

    with open(error_file, "w") as file:
        json.dump(injected_errors, file, indent=4)

    print("Error manifest saved successful")   

if __name__ == "__main__":
    main() 