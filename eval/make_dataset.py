import os
import json
from faker import Faker

fake = Faker(["en_US", "de_DE", "fr_FR"])


def generate_contract(doc_id):
    person = fake.name()
    email = fake.ascii_free_email()
    iban = fake.iban()
    phone = fake.phone_number()

    text = (
        f"EMPLOYMENT AGREEMENT\n\n"
        f"This agreement is made between RedactFlow Corp and the employee {person}.\n"
        f"The employee can be contacted at {email} or via phone at {phone}.\n"
        f"Salary payments will be deposited to the following IBAN: {iban}.\n"
        f"Signed by {person} on this day."
    )

    pii_list = [
        {"type": "PERSON", "text": person},
        {"type": "EMAIL", "text": email},
        {"type": "IBAN", "text": iban},
        {"type": "PHONE", "text": phone}
    ]
    return text, pii_list


def generate_support_ticket(doc_id):
    person = fake.name()
    email = fake.ascii_free_email()
    ip = fake.ipv4()
    card = fake.credit_card_number(card_type="visa")

    text = (
        f"SUPPORT TICKET #{1000 + doc_id}\n\n"
        f"Customer Name: {person}\n"
        f"Email Address: {email}\n"
        f"IP Address: {ip}\n"
        f"Issue: I cannot complete my payment. My credit card number is {card}.\n"
        f"Please resolve this immediately. Regards, {person}."
    )

    pii_list = [
        {"type": "PERSON", "text": person},
        {"type": "EMAIL", "text": email},
        {"type": "IP_ADDRESS", "text": ip},
        {"type": "CREDIT_CARD", "text": card}
    ]
    return text, pii_list


def generate_hr_report(doc_id):
    person = fake.name()
    phone = fake.phone_number()
    email = fake.ascii_free_email()

    text = (
        f"HR PERFORMANCE REVIEW\n\n"
        f"Employee Name: {person}\n"
        f"Contact: {phone} / {email}\n"
        f"Reviewer Comments: {person} has demonstrated exceptional leadership qualities "
        f"this quarter. However, we need to schedule a follow-up call at {phone}."
    )

    pii_list = [
        {"type": "PERSON", "text": person},
        {"type": "EMAIL", "text": email},
        {"type": "PHONE", "text": phone}
    ]
    return text, pii_list


def create_dataset():
    os.makedirs("sample_docs", exist_ok=True)

    generators = [
        ("contract", generate_contract),
        ("ticket", generate_support_ticket),
        ("hr_report", generate_hr_report)
    ]

    for prefix, generator in generators:
        for i in range(10):  # از هر کدوم ۱۰ تا می‌سازیم (در مجموع ۳۰ سند)
            text, pii = generator(i)

            # ذخیره فایل متن
            txt_filename = f"sample_docs/{prefix}_{i}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write(text)

            # ذخیره فایل جواب‌ها (Ground Truth)
            json_filename = f"sample_docs/{prefix}_{i}_ground_truth.json"
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(pii, f, indent=4, ensure_ascii=False)

    print("Successfully generated 30 synthetic documents and ground truths!")


if __name__ == "__main__":
    create_dataset()
