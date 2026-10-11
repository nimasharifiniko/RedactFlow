# 🔒 RedactFlow

**Local-first automated PII redaction pipeline combining regex validation rules with local LLMs.**

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5--Coder-orange)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 The Problem

Organizations need to share contracts, HR files, and support logs with third-party vendors or cloud AI models. However, manually redacting sensitive Personal Identifiable Information (PII) is **slow, tedious, and error-prone**. Leaving a single email or bank account unredacted can lead to severe privacy compliance issues.

**RedactFlow** solves this by offering a zero-data-leakage, local-first redaction tool that automatically detects, masks, and reports sensitive entities before documents leave your infrastructure.

---

## ✨ Key Features

- **🔒 100% Local-First:** No document text or metadata ever leaves your local machine.
- **⚡ Hybrid Detection Engine:**
  - **Deterministic Rules:** Validated regex with mathematical algorithms (`Luhn` for Credit Cards, `mod-97` for IBANs, Google's `phonenumbers` for international phones).
  - **Contextual Local AI:** Runs `Qwen 2.5` via Ollama to detect names (`PERSON`) and physical `ADDRESS` entities.
- **🛡️ Anti-Hallucination Verification:** Strictly verifies LLM outputs against source character offsets to eliminate hallucinated findings.
- **🏷️ Consistent Pseudonymization:** Same entity always maps to the same token (e.g., `Anna Weber` $\rightarrow$ `[PERSON_1]`) maintaining context for downstream AI tools. Optional mapping export for reversible flows.
- **📊 Human-in-the-Loop Review:** Interactive Streamlit interface allows users to review, confirm, or override flagged entities before downloading clean outputs.
- **🧾 Audit Reporting:** Generates anonymous JSON execution logs for compliance tracking.

---

## 📊 Evaluation & Benchmark Results

We evaluated RedactFlow on **30 synthetic documents** (Contracts, HR Reviews, Support Tickets) generated via `Faker`.

| PII Category | Regex-Only Recall | RedactFlow Hybrid Recall | Precision | Status |
| :--- | :---: | :---: | :---: | :--- |
| **EMAIL** | 100.0% | **100.0%** | 100.0% | ✅ Validated Rule |
| **IBAN / Bank** | 100.0% | **100.0%** | 100.0% | ✅ mod-97 Checked |
| **CREDIT_CARD** | 100.0% | **100.0%** | 100.0% | ✅ Luhn Checked |
| **IP_ADDRESS** | 100.0% | **100.0%** | 100.0% | ✅ Range Checked |
| **PERSON (Names)** | **0.0%** | **100.0%** | 50.0%* | 🚀 Local AI Boost |
| **OVERALL SYSTEM** | **60.0%** | **89.1%** | **74.2%** | **+29.1% Total Recall** |

> **Performance:** Average processing time is **~0.67 seconds per document** locally, achieving a **~75x speedup** compared to manual redaction (~50s per doc).  
> *\*Note: Precision favors high-recall safety to prevent accidental leaks over missing entities.*

---

## 🏗️ Architecture
[Document: PDF/DOCX/TXT]
│
▼
[extractors.py]
│
├──────────────────────────┐
▼ ▼
[regex_detector.py] [llm_detector.py]
(High Confidence) (Contextual AI)

Emails / IP - PERSON / ADDRESS
IBAN (mod-97) - Anti-Hallucination
Card (Luhn) - Confidence Scoring
│ │
└────────────┬─────────────┘
▼
[merger.py] (Overlap Resolution)
│
▼
[app.py] (Streamlit Glass UI)
│
┌─────────┴─────────┐
▼ ▼
[redactor.py] [report.py]
(Clean Document) (Audit Metrics JSON)
text


---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai/) installed and running locally.

Pull the local model:
```bash
ollama pull qwen2.5-coder:7b
2. Installation
Bash

# Clone repository
git clone https://github.com/nimasharifiniko/RedactFlow.git
cd RedactFlow

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
3. Run Application
Bash

streamlit run app.py
4. Run Automated Tests & Benchmark
Bash

# Run unit tests
python -m pytest

# Run evaluation benchmark
python -m eval.evaluate
⚠️ Limitations & Disclaimer
Scanned PDFs: Current extractors rely on text-based PDFs (pdfplumber). Scanned image PDFs require an OCR preprocessing step (e.g., tesseract).
Human Review: RedactFlow is a decision-support system designed to reduce manual effort. It does not provide legal guarantees and human review is recommended for high-stakes compliance.
GDPR Compliance: Using this tool reduces privacy risks, but does not automatically confer legal compliance without organizational governance.
👨‍💻 Author
Nima Sharifi Niko
Python AI & Automation Developer

GitHub Profile
LinkedIn Profile
📜 License
Distributed under the MIT License. See LICENSE for more information.