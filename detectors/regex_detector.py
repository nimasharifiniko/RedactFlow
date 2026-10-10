import re
import phonenumbers


def luhn_check(card_number):
    cleaned = "".join(card_number.split())
    if not cleaned.isdigit():
        return False
    digits = [int(d) for d in cleaned]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return total % 10 == 0


def iban_check(iban_str):
    cleaned = "".join(iban_str.split()).upper()
    if len(cleaned) < 4:
        return False
    rearranged = cleaned[4:] + cleaned[:4]
    num_str = ""
    for char in rearranged:
        if char.isdigit():
            num_str += char
        elif char.isalpha():
            num_str += str(ord(char) - ord("A") + 10)
        else:
            return False
    try:
        return int(num_str) % 97 == 1
    except ValueError:
        return False


def detect_emails(text):
    results = []
    email_regex = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    for match in re.finditer(email_regex, text):
        results.append({
            "type": "EMAIL",
            "start": match.start(),
            "end": match.end(),
            "text": match.group(),
            "confidence": "high"
        })
    return results


def detect_ips(text):
    results = []
    ip_regex = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
    for match in re.finditer(ip_regex, text):
        parts = match.group().split(".")
        if all(0 <= int(part) <= 255 for part in parts):
            results.append({
                "type": "IP_ADDRESS",
                "start": match.start(),
                "end": match.end(),
                "text": match.group(),
                "confidence": "high"
            })
    return results


def detect_cards(text):
    results = []
    card_regex = r"\b(?:\d[ -]*?){13,19}\b"
    for match in re.finditer(card_regex, text):
        raw_text = match.group()
        if luhn_check(raw_text):
            results.append({
                "type": "CREDIT_CARD",
                "start": match.start(),
                "end": match.end(),
                "text": raw_text,
                "confidence": "high"
            })
    return results


def detect_ibans(text):
    results = []
    # ریجکس جدید که فاصله‌ها و خط تیره‌ها را هم در IBAN پوشش می‌دهد
    iban_regex = r"\b[A-Z]{2}[0-9]{2}(?:[ -]?[A-Z0-9]){11,30}\b"
    for match in re.finditer(iban_regex, text, re.IGNORECASE):
        raw_text = match.group()
        if iban_check(raw_text):
            results.append({
                "type": "IBAN",
                "start": match.start(),
                "end": match.end(),
                "text": raw_text,
                "confidence": "high"
            })
    return results


def detect_phones(text):
    results = []
    for match in phonenumbers.PhoneNumberMatcher(text, None):
        results.append({
            "type": "PHONE",
            "start": match.start,
            "end": match.end,
            "text": match.raw_string,
            "confidence": "high"
        })
    return results


def detect_structured_pii(text):
    all_findings = []
    all_findings.extend(detect_emails(text))
    all_findings.extend(detect_ips(text))
    all_findings.extend(detect_cards(text))
    all_findings.extend(detect_ibans(text))
    all_findings.extend(detect_phones(text))

    all_findings.sort(key=lambda x: x["start"])
    return all_findings
