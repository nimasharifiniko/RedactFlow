import json


def redact_text(text, findings, generate_mapping=False):
    type_counters = {}
    entity_to_token = {}

    # keep tokens consistent so same name always gets same tag
    for item in findings:
        pii_type = item["type"]
        raw_text = item["text"]
        key = (pii_type, raw_text.strip().lower())

        if key not in entity_to_token:
            type_counters[pii_type] = type_counters.get(pii_type, 0) + 1
            token = f"[{pii_type}_{type_counters[pii_type]}]"
            entity_to_token[key] = (token, raw_text)

    # replace from end to start so character offsets don't shift
    sorted_findings = sorted(findings, key=lambda x: x["start"], reverse=True)

    redacted = text
    for item in sorted_findings:
        key = (item["type"], item["text"].strip().lower())
        token, _ = entity_to_token.get(
            key, (f"[{item['type']}]", item["text"]))
        redacted = redacted[:item["start"]] + token + redacted[item["end"]:]

    mapping = {}
    if generate_mapping:
        # only save mapping when pseudonymization mode is on
        mapping = {token: orig_text for (
            token, orig_text) in entity_to_token.values()}

    return redacted, mapping


def restore_text(redacted_text, mapping):
    restored = redacted_text
    for token, original in mapping.items():
        restored = restored.replace(token, original)
    return restored
