
import pandas as pd


def calculate_quality_score(records, errors, entity_name):
    """
    Calculate the percentage of records without validation issues.
    """

    total_records = len(records)

    if total_records == 0:
        return {
            "entity": entity_name,
            "total_records": 0,
            "affected_records": 0,
            "clean_records": 0,
            "quality_score": 0.0
        }

    # Collect IDs of records that have at least one validation issue.
    affected_ids = {
    error["record_id"]
    for error in errors
    if error["entity"] == entity_name
}

    affected_records = len(affected_ids)
    clean_records = max(0, total_records - affected_records)

    score = (clean_records / total_records) * 100

    return {
        "entity": entity_name,
        "total_records": total_records,
        "affected_records": affected_records,
        "clean_records": clean_records,
        "quality_score": round(score, 2)
    }


def calculate_overall_score(entity_scores):
    total_records = sum(
        item["total_records"] for item in entity_scores
    )

    clean_records = sum(
        item["clean_records"] for item in entity_scores
    )

    if total_records == 0:
        return 0.0

    return round((clean_records / total_records) * 100, 2)



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
