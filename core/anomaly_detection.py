
import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_invoice_anomalies(invoices, contamination=0.01):
    required_columns = {"legacy_invoice_id", "amount"}

    missing_columns = required_columns - set(invoices.columns)

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    result = invoices.copy()

    # Convert invoice amounts into numbers.
    result["amount"] = pd.to_numeric(
        result["amount"], errors="coerce"
    )

    # Default: records are not flagged.
    result["is_anomaly"] = False
    result["anomaly_score"] = float("nan")

    # Only positive, valid amounts are analysed.
    valid_records = result["amount"].notna() & (result["amount"] > 0)

    if valid_records.sum() < 10:
        return result

    # Create and train the Isolation Forest model.
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42
    )

    amounts = result.loc[valid_records, ["amount"]]

    predictions = model.fit_predict(amounts)
    scores = model.decision_function(amounts)

    # -1 means anomaly; 1 means normal.
    result.loc[valid_records, "is_anomaly"] = predictions == -1
    result.loc[valid_records, "anomaly_score"] = scores

    return result
