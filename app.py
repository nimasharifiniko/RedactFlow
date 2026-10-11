import streamlit as st
import os
import time
import json
from extractors import extract_text
from merger import scan_document
from redactor import redact_text
from report import generate_report

st.set_page_config(page_title="RedactFlow | Nima Sharifi Niko",
                   page_icon="🔒", layout="wide")

# CSS خیلی محدود فقط برای استایل متن‌های هایلایت‌شده و پروفایل
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap');
    
    .classic-title {
        font-family: 'Cinzel', serif;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .profile-link {
        color: #FF4500 !important;
        text-decoration: none;
        font-weight: bold;
        margin: 0 10px;
    }
    .profile-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# رنگ‌های لایت و زیبا برای هایلایت داخل متن
TYPE_COLORS = {
    "PERSON": "#FFB3B3",
    "EMAIL": "#A7F3D0",
    "PHONE": "#BAE6FD",
    "IBAN": "#D9F99D",
    "CREDIT_CARD": "#FEF08A",
    "IP_ADDRESS": "#E9D5FF",
    "ADDRESS": "#FED7AA",
}


def highlight_text(text, findings):
    if not findings:
        return text
    sorted_f = sorted(findings, key=lambda x: x["start"], reverse=True)
    result = text
    for item in sorted_f:
        color = TYPE_COLORS.get(item["type"], "#E2E8F0")
        original = result[item["start"]:item["end"]]
        tag = f'<span style="background-color:{color}; color:#0F172A; padding:2px 4px; border-radius:4px; font-weight:600; border-bottom: 2px solid #FF4500;" title="{item["type"]}">{original}</span>'
        result = result[:item["start"]] + tag + result[item["end"]:]
    return result


def main():
    # هدر اصلی
    st.markdown('<h1 class="classic-title">🔒 REDACTFLOW</h1>',
                unsafe_allow_html=True)
    st.caption(
        "Local-first document redaction. Hybrid engine (Regex + AI). Nothing leaves your machine.")

    # سایدبار
    with st.sidebar:
        st.markdown(
            '<h2 class="classic-title" style="text-align: center; font-size: 22px;">REDACTFLOW</h2>', unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align: center; font-size: 13px; color: #64748B;">Developed by Nima Sharifi Niko</p>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center;"><a href="https://github.com/nimasharifiniko" target="_blank" class="profile-link">GitHub</a> | <a href="https://www.linkedin.com/in/nima-sharifiniko/" target="_blank" class="profile-link">LinkedIn</a></div>', unsafe_allow_html=True)
        st.divider()

        st.subheader("⚙️ Engine Settings")
        use_llm = st.toggle("Enable Local AI (Ollama)", value=True)
        generate_map = st.toggle("Generate Mapping (Reversible)", value=False)
        st.divider()

        st.subheader("🎯 PII to Detect")
        active_types = set()

        st.write("**High Priority (Rules)**")
        if st.checkbox("Emails", value=True):
            active_types.add("EMAIL")
        if st.checkbox("Phone Numbers", value=True):
            active_types.add("PHONE")
        if st.checkbox("IBAN / Bank", value=True):
            active_types.add("IBAN")
        if st.checkbox("Credit Cards", value=True):
            active_types.add("CREDIT_CARD")
        if st.checkbox("IP Addresses", value=True):
            active_types.add("IP_ADDRESS")

        st.write("")
        st.write("**Contextual (AI)**")
        if st.checkbox("Names (PERSON)", value=True):
            active_types.add("PERSON")
        if st.checkbox("Addresses", value=True):
            active_types.add("ADDRESS")

    # آپلود فایل
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["txt", "pdf", "docx"],
        help="Supported: TXT, PDF (text-based), DOCX"
    )

    if uploaded_file is not None:
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # دکمه با رنگ نارنجی جیغ (اتوماتیک از config خوانده می‌شود)
        if st.button("🔍 Analyze Document", type="primary"):
            with st.spinner("Analyzing securely on your local machine..."):
                start_time = time.time()
                text = extract_text(temp_path)
                findings = scan_document(text, use_llm=use_llm)
                findings = [f for f in findings if f["type"] in active_types]
                processing_time = time.time() - start_time
                redacted_text, mapping = redact_text(
                    text, findings, generate_mapping=generate_map)
                report = generate_report(
                    findings, processing_time, uploaded_file.name)

                st.session_state["original_text"] = text
                st.session_state["redacted_text"] = redacted_text
                st.session_state["findings"] = findings
                st.session_state["report"] = report
                st.session_state["filename"] = uploaded_file.name

        if "findings" in st.session_state:
            findings = st.session_state["findings"]
            report = st.session_state["report"]
            original_text = st.session_state["original_text"]
            redacted_text = st.session_state["redacted_text"]

            st.divider()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Entities Found", report["total_entities_found"])
            c2.metric("Flagged for Review", report["flagged_for_human_review"])
            c3.metric("Processing Time",
                      f"{report['processing_time_seconds']}s")
            c4.metric("PII Types", len(report["breakdown_by_type"]))

            st.divider()

            left_col, right_col = st.columns(2)

            with left_col:
                st.subheader("📄 Original (Highlighted)")
                html = highlight_text(original_text, findings)
                st.markdown(
                    f'<div style="background-color: #FFFFFF; border: 1px solid #D1D5DB; border-radius: 8px; padding: 15px; font-family: monospace; white-space: pre-wrap; line-height: 1.8;">{html}</div>',
                    unsafe_allow_html=True
                )

            with right_col:
                st.subheader("🔒 Redacted Document")
                st.markdown(
                    f'<div style="background-color: #FFFFFF; border: 1px solid #D1D5DB; border-radius: 8px; padding: 15px; font-family: monospace; white-space: pre-wrap; line-height: 1.8; color: #0F172A;">{redacted_text}</div>',
                    unsafe_allow_html=True
                )

            st.divider()
            dl1, dl2 = st.columns(2)
            fname = st.session_state.get("filename", "document.txt")
            with dl1:
                st.download_button("📥 Download Redacted", data=redacted_text,
                                   file_name=f"redacted_{fname}", mime="text/plain")
            with dl2:
                report_json = json.dumps(report, indent=2, ensure_ascii=False)
                st.download_button("📊 Download Audit Report", data=report_json,
                                   file_name=f"report_{fname}.json", mime="application/json")


if __name__ == "__main__":
    main()
