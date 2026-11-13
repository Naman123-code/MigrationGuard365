from rapidfuzz import process, fuzz

CUSTOMER_MAPPING = {
    "cust_id": "legacy_customer_id",
    "cust_nm": "name",
    "email": "email",
    "tax_no": "tax_id",
    "phone": "phone",
    "country": "country",
    "postal_code": "postal_code"
}

VENDOR_MAPPING = {
    "vendor_id": "legacy_vendor_id",
    "vendor_nm": "name",
    "email": "email",
    "tax_no": "tax_id",
    "phone": "phone",
    "country": "country",
    "postal_code": "postal_code"
}

INVOICE_MAPPING = {
    "inv_id": "legacy_invoice_id",
    "inv_no": "invoice_number",
    "cust_id": "customer_legacy_id",
    "vendor_id": "vendor_legacy_id",
    "inv_dt": "invoice_date",
    "inv_amt": "amount",
    "currency": "currency"
}

def apply_mapping(dataframe, mapping):
    mapped_df = dataframe.rename(columns=mapping)
    return mapped_df

def suggest_mapping(source_columns, target_columns, threshold=70):
    suggestions = {}

    for column in source_columns:
        match = process.extractOne(
            column,
            target_columns,
            scorer=fuzz.WRatio
        )

        if match and match[1] >= threshold:
            suggestions[column] = {
                "suggested_target": match[0],
                "confidence": match[1]
            }

    return suggestions

if __name__ == "__main__":
    import pandas as pd

    source_columns = [
        "customer_name",
        "customer_tax_id",
        "customer_email",
        "random_field"
    ]

    target_columns = [
        "name",
        "tax_id",
        "email",
        "phone"
    ]

    suggestions = suggest_mapping(source_columns, target_columns)

    print("\nIntelligent Mapping Suggestions:")
    print(suggestions)

    # sample_data = pd.DataFrame({
    #     "cust_id": ["CUST001"],
    #     "cust_nm": ["Rahul Sharma"],
    #     "tax_no": ["ABC123"]
    # })

    # result = apply_mapping(sample_data, CUSTOMER_MAPPING)

    # print(result)

