import os
import json
import glob
import time
from merger import scan_document
from extractors import extract_text


def evaluate_system(use_llm=True):
    doc_files = glob.glob("sample_docs/*.txt")
    if not doc_files:
        print("No documents found in sample_docs/. Run make_dataset.py first.")
        return

    # فیلتر کردن فایل‌های تست اصلی (صرف نظر از فایل‌های متفرقه)
    eval_docs = [f for f in doc_files if os.path.exists(
        f.replace(".txt", "_ground_truth.json"))]
    print(f"Evaluating {len(eval_docs)} documents with LLM = {use_llm} ...\n")

    stats = {}

    def get_stat_bucket(category):
        if category not in stats:
            stats[category] = {"tp": 0, "fp": 0, "fn": 0}
        return stats[category]

    start_time = time.time()

    for doc_path in eval_docs:
        gt_path = doc_path.replace(".txt", "_ground_truth.json")
        text = extract_text(doc_path)
        with open(gt_path, "r", encoding="utf-8") as f:
            ground_truth = json.load(f)

        # اجرای اسکن هیبریدی
        detected_items = scan_document(text, use_llm=use_llm)

        matched_gt_indices = set()
        matched_detected_indices = set()

        for d_idx, d_item in enumerate(detected_items):
            d_text_clean = d_item["text"].strip().lower()
            found_match = False
            for g_idx, g_item in enumerate(ground_truth):
                if g_idx in matched_gt_indices:
                    continue
                g_text_clean = g_item["text"].strip().lower()

                if d_text_clean in g_text_clean or g_text_clean in d_text_clean:
                    matched_gt_indices.add(g_idx)
                    matched_detected_indices.add(d_idx)
                    bucket = get_stat_bucket(g_item["type"])
                    bucket["tp"] += 1
                    found_match = True
                    break

            if not found_match:
                bucket = get_stat_bucket(d_item["type"])
                bucket["fp"] += 1

        for g_idx, g_item in enumerate(ground_truth):
            if g_idx not in matched_gt_indices:
                bucket = get_stat_bucket(g_item["type"])
                bucket["fn"] += 1

    elapsed_time = time.time() - start_time

    # چاپ گزارش نتایج
    print("=" * 65)
    print(f"{'CATEGORY':<15} | {'PRECISION':<12} | {'RECALL':<12} | {'SAMPLES'}")
    print("-" * 65)

    total_tp = sum(s["tp"] for s in stats.values())
    total_fp = sum(s["fp"] for s in stats.values())
    total_fn = sum(s["fn"] for s in stats.values())

    for cat, s in sorted(stats.items()):
        precision = (s["tp"] / (s["tp"] + s["fp"])) * \
            100 if (s["tp"] + s["fp"]) > 0 else 0.0
        recall = (s["tp"] / (s["tp"] + s["fn"])) * \
            100 if (s["tp"] + s["fn"]) > 0 else 0.0
        total_samples = s["tp"] + s["fn"]
        print(f"{cat:<15} | {precision:>9.1f}% | {recall:>9.1f}% | {total_samples:>5}")

    print("-" * 65)
    overall_prec = (total_tp / (total_tp + total_fp)) * \
        100 if (total_tp + total_fp) > 0 else 0.0
    overall_rec = (total_tp / (total_tp + total_fn)) * \
        100 if (total_tp + total_fn) > 0 else 0.0
    print(f"{'OVERALL':<15} | {overall_prec:>9.1f}% | {overall_rec:>9.1f}% | {total_tp + total_fn:>5}")
    print("=" * 65)
    print(
        f"Processed in: {elapsed_time:.2f} seconds ({elapsed_time/len(eval_docs):.2f}s per doc)")


if __name__ == "__main__":
    evaluate_system(use_llm=True)
