import json
import re
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

MODEL_NAME = "qwen2.5-coder:7b"


def split_into_chunks(text, chunk_size=1500, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append((text[start:end], start))
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks


def extract_entities_from_chunk(chunk_text, chunk_offset):
    system_prompt = (
        "You are an expert privacy tool. Extract only PERSON names and physical ADDRESS entities from the text.\n"
        "Return ONLY a valid JSON object in this exact format:\n"
        "{\"entities\": [{\"type\": \"PERSON\", \"text\": \"Full Name\"}, {\"type\": \"ADDRESS\", \"text\": \"Full Address\"}]}\n"
        "If no names or addresses exist, return {\"entities\": []}."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk_text}
            ]
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        raw_entities = parsed.get("entities", [])
    except Exception:
        return []

    verified_entities = []

    for item in raw_entities:
        ent_type = item.get("type", "").upper()
        ent_text = item.get("text", "").strip()

        if not ent_text or ent_type not in ["PERSON", "ADDRESS"]:
            continue

        # بررسی وجود متن در سند اصلی برای حذف توهم‌های مدل (Anti-Hallucination)
        for match in re.finditer(re.escape(ent_text), chunk_text):
            start_in_chunk = match.start()
            end_in_chunk = match.end()

            global_start = chunk_offset + start_in_chunk
            global_end = chunk_offset + end_in_chunk

            # تعیین سطح اطمینان
            confidence = "medium"
            if len(ent_text.split()) < 2 and ent_type == "PERSON":
                confidence = "low"

            verified_entities.append({
                "type": ent_type,
                "start": global_start,
                "end": global_end,
                "text": ent_text,
                "confidence": confidence
            })

    return verified_entities


def detect_llm_pii(text):
    chunks = split_into_chunks(text)
    all_findings = []

    for chunk_text, chunk_offset in chunks:
        findings = extract_entities_from_chunk(chunk_text, chunk_offset)
        all_findings.extend(findings)

    # حذف موارد تکراری ناشی از هم‌پوشانی Chunks
    unique_findings = []
    seen = set()
    for item in all_findings:
        key = (item["type"], item["start"], item["end"])
        if key not in seen:
            seen.add(key)
            unique_findings.append(item)

    unique_findings.sort(key=lambda x: x["start"])
    return unique_findings
