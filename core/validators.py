
import re
import yaml
import math

from pathlib import Path
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from rapidfuzz import fuzz


# 1. LOAD VALIDATION RULES

def load_validation_rules():
    config_path = Path(__file__).parent / "rules_config.yaml"

    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config["rules"]


# 2. HANDLE MISSING VALUES

def is_missing(value):
    if value is None:
        return True

    if isinstance(value, float) and math.isnan(value):
        return True

    return str(value).strip() == ""


# 3. VALIDATION CHECKS

def run_validation_check(rule, record, context):
    field = rule["field"]
    value = record.get(field)
    rule_type = rule["type"]

    # Required field
    if rule_type == "required":
        return is_missing(value)

        # Customer creation date validation
    if rule_type == "valid_date":
        if is_missing(value):
            return True

        try:
            datetime.strptime(str(value).strip(), "%Y-%m-%d")
            return False
        except ValueError:
            return True

    # Tax ID: basic alphanumeric format
    if rule_type == "tax_id":
        if is_missing(value):
            return False

        return not bool(re.fullmatch(r"[A-Za-z0-9]{6,20}", str(value).strip()))

    # Email format
    
    # Email format
    if rule_type == "email":
        if is_missing(value):
            return False

        pattern = r"^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$"
        return not bool(re.fullmatch(pattern, str(value).strip()))

    # Phone number
    if rule_type == "phone":
        if is_missing(value):
            return False

        phone = str(value).strip()

        # Remove extensions such as x123, ext. 123
        phone = re.split(
            r"\s*(?:x|ext\.?|extension)\s*",
            phone,
            flags=re.IGNORECASE
        )[0]

        digits = re.sub(r"\D", "", phone)

        return not (7 <= len(digits) <= 15)

    
    # Country code validation
    if rule_type == "country":
        if is_missing(value):
            return True

        supported_countries = {"IN"}

        return str(value).strip().upper() not in supported_countries




    # Duplicate vendor
    if rule_type == "duplicate_vendor":
        vendors = context.get("vendors", [])

        for vendor in vendors:
            if vendor is record:
                continue

            tax_id = record.get("tax_id")
            other_tax_id = vendor.get("tax_id")

            if not is_missing(tax_id) and str(tax_id).strip().lower() == str(other_tax_id).strip().lower():
                return True

            name = str(record.get("name", "")).strip().lower()
            other_name = str(vendor.get("name", "")).strip().lower()

            postal = record.get("postal_code")
            other_postal = vendor.get("postal_code")

            if (
                name
                and other_name
                and not is_missing(postal)
                and postal == other_postal
                and fuzz.ratio(name, other_name) > 90
            ):
                return True

        return False

    # Invoice customer/vendor references
    if rule_type == "invoice_references":
        customer_ids = context.get("customer_ids", set())
        vendor_ids = context.get("vendor_ids", set())

        customer_missing = (
            record.get("customer_legacy_id") not in customer_ids
        )

        vendor_missing = (
            record.get("vendor_legacy_id") not in vendor_ids
        )

        return customer_missing or vendor_missing

    # Positive invoice amount
    if rule_type == "positive_number":
        try:
            return Decimal(str(value)) <= 0
        except (InvalidOperation, TypeError):
            return True

    # Supported currencies
    if rule_type == "currency":
        return str(value).strip().upper() not in {"INR", "USD", "EUR"}

    # Valid date and not in future
    if rule_type == "date_not_future":
        try:
            parsed_date = datetime.strptime(
                str(value).strip(), "%d/%m/%Y"
            ).date()
        except ValueError:
            try:
                parsed_date = date.fromisoformat(str(value).strip())
            except ValueError:
                return True

        return parsed_date > date.today()

    # Duplicate invoice
    if rule_type == "duplicate_invoice":
        invoices = context.get("invoices", [])

        for invoice in invoices:
            if invoice is record:
                continue

            if (
                invoice.get("invoice_number") == record.get("invoice_number")
                and invoice.get("vendor_legacy_id") == record.get("vendor_legacy_id")
                and invoice.get("amount") == record.get("amount")
            ):
                return True

        return False

    # Extreme invoice amount
    if rule_type == "amount_outlier":
        try:
            amount = float(value)
            amounts = context.get("vendor_amounts", {}).get(
                record.get("vendor_legacy_id"), []
            )

            if len(amounts) < 2:
                return False

            mean = sum(amounts) / len(amounts)
            variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
            std_dev = math.sqrt(variance)

            return std_dev > 0 and amount > mean + (3 * std_dev)

        except (ValueError, TypeError):
            return False

    # Unique source identifier
    if rule_type == "unique":
        ids = context.get("invoice_ids", [])

        return ids.count(value) > 1

    raise ValueError(f"Unknown validation type: {rule_type}")


# 4. CENTRAL VALIDATION ENGINE

def validate_record(record, entity, context=None):
    errors = []
    context = context or {}

    rules = load_validation_rules()

    for rule in rules:

        if not rule["enabled"]:
            continue

        if rule["entity"] != entity:
            continue

        failed = run_validation_check(rule, record, context)

        if failed:
            errors.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "field": rule["field"],
                "message": rule["description"],
                "severity": rule["severity"],
                "action": rule["action"]
            })

    return errors
