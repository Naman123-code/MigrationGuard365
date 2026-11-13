

from datetime import date, timedelta

from core.validators import load_validation_rules, run_validation_check

rules = {
    rule["id"]: rule
    for rule in load_validation_rules()
}

# ---------------------------------------
# NEGATIVE TESTS: INVALID RECORDS
# ---------------------------------------

customer = {
    "name": "",
    "tax_id": None,
    "email": "invalid-email",
    "phone": "123",
    "country": "XX"
}

vendor = {
    "name": "",
    "tax_id": None,
    "phone": "ABC123"
}

duplicate_vendor = {
    "name": "ABC Technologies",
    "tax_id": None,
    "postal_code": "201301"
}

original_vendor = {
    "name": "ABC Technologies",
    "tax_id": None,
    "postal_code": "201301"
}

invoice = {
    "customer_legacy_id": "CUST999",
    "vendor_legacy_id": "VEND999",
    "amount": "-500",
    "currency": "XYZ",
    "invoice_date": (
        date.today() + timedelta(days=1)
    ).strftime("%d/%m/%Y"),
    "invoice_number": "INV100",
    "legacy_invoice_id": "INV001"
}

duplicate_invoice = {
    "invoice_number": "INV100",
    "vendor_legacy_id": "VEND001",
    "amount": "5000"
}

original_invoice = {
    "invoice_number": "INV100",
    "vendor_legacy_id": "VEND001",
    "amount": "5000"
}

test_cases = [
    ("V01", customer, {}),
    ("V02", customer, {}),
    ("V03", customer, {}),
    ("V04", customer, {}),
    ("V05", customer, {}),
    ("V06", vendor, {}),
    ("V07", vendor, {}),
    ("V08", vendor, {}),
    ("V09", duplicate_vendor, {
        "vendors": [original_vendor, duplicate_vendor]
    }),
    ("V10", invoice, {
        "customer_ids": {"CUST001"},
        "vendor_ids": {"VEND001"}
    }),
    ("V11", invoice, {}),
    ("V12", invoice, {}),
    ("V13", invoice, {}),
    ("V14", duplicate_invoice, {
        "invoices": [original_invoice, duplicate_invoice]
    }),
    ("V15", {
        "amount": "10000000",
        "vendor_legacy_id": "VEND001"
    }, {
        "vendor_amounts": {
            "VEND001": [900, 1000, 1100, 1050, 950]
        }
    })
]

print("\nMIGRATIONGUARD 365 - NEGATIVE TEST RESULTS\n")

passed = 0
failed = 0

for rule_id, record, context in test_cases:
    try:
        result = run_validation_check(
            rules[rule_id], record, context
        )

        if result is True:
            print(f"{rule_id} - PASS")
            passed += 1
        else:
            print(f"{rule_id} - FAIL (Expected True, got {result})")
            failed += 1

    except Exception as error:
        print(f"{rule_id} - ERROR: {error}")
        failed += 1

print("\n--------------------------------")
print(f"Negative tests: {len(test_cases)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print("--------------------------------")


# ---------------------------------------
# POSITIVE TESTS: VALID RECORDS
# ---------------------------------------

valid_customer = {
    "name": "Rahul Sharma",
    "tax_id": "ABCDE1234F",
    "email": "rahul@gmail.com",
    "phone": "9876543210",
    "country": "IN"
}

valid_vendor = {
    "name": "Fresh Technologies",
    "tax_id": "VEND12345",
    "phone": "9876543210",
    "postal_code": "201301"
}

valid_invoice = {
    "customer_legacy_id": "CUST001",
    "vendor_legacy_id": "VEND001",
    "amount": "5000",
    "currency": "INR",
    "invoice_date": (
        date.today() - timedelta(days=1)
    ).strftime("%d/%m/%Y"),
    "invoice_number": "INV200",
    "legacy_invoice_id": "INV200"
}

valid_duplicate_vendor_context = {
    "vendors": [
        {
            "name": "Other Solutions",
            "tax_id": "DIFFERENT123",
            "postal_code": "110001"
        }
    ]
}

valid_duplicate_invoice_context = {
    "invoices": [
        {
            "invoice_number": "INV999",
            "vendor_legacy_id": "VEND002",
            "amount": "8000"
        }
    ]
}

valid_test_cases = [
    ("V01", valid_customer, {}),
    ("V02", valid_customer, {}),
    ("V03", valid_customer, {}),
    ("V04", valid_customer, {}),
    ("V05", valid_customer, {}),
    ("V06", valid_vendor, {}),
    ("V07", valid_vendor, {}),
    ("V08", valid_vendor, {}),
    ("V09", valid_vendor, valid_duplicate_vendor_context),
    ("V10", valid_invoice, {
        "customer_ids": {"CUST001"},
        "vendor_ids": {"VEND001"}
    }),
    ("V11", valid_invoice, {}),
    ("V12", valid_invoice, {}),
    ("V13", valid_invoice, {}),
    ("V14", valid_invoice, valid_duplicate_invoice_context),
    ("V15", {
        "amount": "1000",
        "vendor_legacy_id": "VEND001"
    }, {
        "vendor_amounts": {
            "VEND001": [900, 1000, 1100]
        }
    })
]

print("\nMIGRATIONGUARD 365 - POSITIVE TEST RESULTS\n")

positive_passed = 0
positive_failed = 0

for rule_id, record, context in valid_test_cases:
    try:
        result = run_validation_check(
            rules[rule_id], record, context
        )

        if result is False:
            print(f"{rule_id} - PASS")
            positive_passed += 1
        else:
            print(f"{rule_id} - FAIL (Expected False, got {result})")
            positive_failed += 1

    except Exception as error:
        print(f"{rule_id} - ERROR: {error}")
        positive_failed += 1

print("\n--------------------------------")
print(f"Positive tests: {len(valid_test_cases)}")
print(f"Passed: {positive_passed}")
print(f"Failed: {positive_failed}")
print("--------------------------------")

# VENDOR PHONE DEBUG TEST

vendor_phone_rule = rules["V08"]

test_vendor_phone = {
    "phone": "ABC123"
}

valid_vendor_phone = {
    "phone": "9876543210"
}

print("\nVENDOR PHONE DEBUG")

print(
    "Invalid phone:",
    run_validation_check(
        vendor_phone_rule,
        test_vendor_phone,
        {}
    )
)

print(
    "Valid phone:",
    run_validation_check(
        vendor_phone_rule,
        valid_vendor_phone,
        {}
    )
)

# CUSTOMER CREATION DATE TESTS

date_rule = rules["V16"]

valid_date_record = {
    "created_date": "2026-10-15"
}

invalid_date_record = {
    "created_date": "not-a-date"
}

print("\nCUSTOMER CREATION DATE TESTS")

print(
    "Valid date:",
    "PASS" if not run_validation_check(
        date_rule, valid_date_record, {}
    ) else "FAIL"
)

print(
    "Invalid date:",
    "PASS" if run_validation_check(
        date_rule, invalid_date_record, {}
    ) else "FAIL"
)