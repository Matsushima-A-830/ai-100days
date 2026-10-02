"""Day 004: キーワードルールベース分類 vs Jeff(Jeff-Qwen3.5-0.8B)ゼロショット分類の比較。

事前に `jeff-serve` を http://localhost:8765 で起動しておくこと
(README: JEFF_CHECKPOINT=<ダウンロードした重み> PORT=8765 jeff-serve)。
実行: python3.13 run_compare.py
"""
import json
import time

from dataset import DATASET, LABELS
from jeff_client import Client, choice_question
from rule_based import classify as rule_classify

JEFF_URL = "http://localhost:8765"
JEFF_MODEL = "jeff-qwen3.5-0.8b"


def run_rule_based():
    results = []
    for item in DATASET:
        t0 = time.perf_counter()
        pred = rule_classify(item["text"])
        dt = time.perf_counter() - t0
        results.append({**item, "pred": pred, "correct": pred == item["true_label"], "latency_sec": dt})
    return results


def run_jeff():
    jeff = Client(JEFF_URL, model=JEFF_MODEL)
    results = []
    for item in DATASET:
        t0 = time.perf_counter()
        choice = jeff.choose(item["text"], LABELS, "Which category best fits this customer support ticket?")
        dt = time.perf_counter() - t0
        results.append({**item, "pred": choice.key, "correct": choice.key == item["true_label"],
                        "probability": choice.probability, "confidence": choice.confidence,
                        "ranked": choice.ranked(), "latency_sec": dt})
    return results


def summarize(name, results):
    n = len(results)
    correct = sum(r["correct"] for r in results)
    easy = [r for r in results if r["group"] == "easy"]
    adv = [r for r in results if r["group"] == "adversarial"]
    easy_acc = sum(r["correct"] for r in easy) / len(easy)
    adv_acc = sum(r["correct"] for r in adv) / len(adv)
    avg_latency = sum(r["latency_sec"] for r in results) / n
    print(f"\n=== {name} ===")
    print(f"overall accuracy: {correct}/{n} = {correct / n:.1%}")
    print(f"  easy group:        {sum(r['correct'] for r in easy)}/{len(easy)} = {easy_acc:.1%}")
    print(f"  adversarial group: {sum(r['correct'] for r in adv)}/{len(adv)} = {adv_acc:.1%}")
    print(f"average latency: {avg_latency * 1000:.2f} ms/decision (total {sum(r['latency_sec'] for r in results):.3f}s for {n} decisions)")
    return {"name": name, "n": n, "correct": correct, "accuracy": correct / n,
            "easy_accuracy": easy_acc, "adv_accuracy": adv_acc, "avg_latency_sec": avg_latency}


def print_mismatches(name, results):
    mism = [r for r in results if not r["correct"]]
    if not mism:
        print(f"  ({name}: no mismatches)")
        return
    print(f"  {name} mismatches:")
    for r in mism:
        print(f"    - text: {r['text']!r}")
        print(f"      true={r['true_label']!r} pred={r['pred']!r}")


if __name__ == "__main__":
    rule_results = run_rule_based()
    jeff_results = run_jeff()

    rule_summary = summarize("Rule-based (keyword matching)", rule_results)
    print_mismatches("rule-based", rule_results)
    jeff_summary = summarize("Jeff-Qwen3.5-0.8B (zero-shot)", jeff_results)
    print_mismatches("jeff", jeff_results)

    with open("compare_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "rule_based": {"summary": rule_summary, "results": rule_results},
            "jeff": {"summary": jeff_summary, "results": jeff_results},
        }, f, ensure_ascii=False, indent=2)
    print("\nWrote compare_results.json")
