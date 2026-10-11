import json
import time
from collections import Counter


def generate_report(findings, processing_time, source_filename="unknown"):
    type_counts = Counter(item["type"] for item in findings)

    flagged_for_review = [
        item for item in findings if item.get("confidence") == "low"
    ]

    report = {
        "source_file": source_filename,
        "total_entities_found": len(findings),
        "breakdown_by_type": dict(type_counts),
        "flagged_for_human_review": len(flagged_for_review),
        "processing_time_seconds": round(processing_time, 3),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }

    return report


def save_report(report, output_path="report.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
