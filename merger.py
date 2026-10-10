from detectors.regex_detector import detect_structured_pii
from detectors.llm_detector import detect_llm_pii


CONFIDENCE_PRIORITY = {
    "high": 3,
    "medium": 2,
    "low": 1
}


def is_overlapping(span1, span2):
    return max(span1["start"], span2["start"]) < min(span1["end"], span2["end"])


def resolve_overlap(item1, item2):
    p1 = CONFIDENCE_PRIORITY.get(item1["confidence"], 1)
    p2 = CONFIDENCE_PRIORITY.get(item2["confidence"], 1)

    if p1 > p2:
        return item1
    elif p2 > p1:
        return item2
    else:
        # اگر اعتبار برابر بود، موردی که طول بیشتری داره رو نگه می‌داریم
        len1 = item1["end"] - item1["start"]
        len2 = item2["end"] - item2["start"]
        return item1 if len1 >= len2 else item2


def merge_detections(regex_items, llm_items):
    combined = sorted(regex_items + llm_items,
                      key=lambda x: (x["start"], -x["end"]))

    if not combined:
        return []

    merged = [combined[0]]

    for current in combined[1:]:
        previous = merged[-1]

        if is_overlapping(previous, current):
            winner = resolve_overlap(previous, current)
            merged[-1] = winner
        else:
            merged.append(current)

    return merged


def scan_document(text, use_llm=True):
    regex_findings = detect_structured_pii(text)

    if not use_llm:
        return regex_findings

    llm_findings = detect_llm_pii(text)
    return merge_detections(regex_findings, llm_findings)
