"""
Day 028 追加検証(ローカルGPU): DenseRAGMemory(埋め込み+クロスエンコーダ再ランキング)を
MutatingSummaryMemory/AppendOnlyMemory/RawRAGMemory(TF-IDF版)と同じ質問セット・同じ
採点方法で比較する。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 親の day-028/ を参照

from datasets import CONVERSATIONS, QUESTIONS
from memory_methods import MutatingSummaryMemory, AppendOnlyMemory, RawRAGMemory
from dense_rag_memory import DenseRAGMemory


def fuzzy_match(gold, value):
    if value is None:
        return False
    if isinstance(value, list):
        return any(fuzzy_match(gold, v) for v in value)
    g = gold.lower()
    v = str(value).lower()
    return g in v or v in g


def run(top_k, candidate_k, use_reranker, label):
    conv_by_id = {c["id"]: c for c in CONVERSATIONS}
    memories = {}
    for conv in CONVERSATIONS:
        rag = DenseRAGMemory(
            conv["turns"], top_k=top_k, candidate_k=candidate_k, use_reranker=use_reranker,
        )
        memories[conv["id"]] = rag

    results = []
    for q in QUESTIONS:
        rag = memories[q["conv_id"]]
        rag_text, rag_qtime, rag_top = rag.answer(q["category"], q["type"], q["question"])
        rag_correct = fuzzy_match(q["gold"], rag_text)
        results.append({**q, "rag_correct": rag_correct, "rag_qtime_ms": rag_qtime * 1000})

    out = {}
    for qtype in ["current", "historical"]:
        subset = [r for r in results if r["type"] == qtype]
        n = len(subset)
        acc = sum(r["rag_correct"] for r in subset) / n
        out[qtype] = acc
    overall = sum(r["rag_correct"] for r in results) / len(results)
    avg_qtime = sum(r["rag_qtime_ms"] for r in results) / len(results)
    print(
        f"[{label}] top_k={top_k} candidate_k={candidate_k} reranker={use_reranker} | "
        f"current acc={out['current']:.2%} | historical acc={out['historical']:.2%} | "
        f"overall acc={overall:.2%} | avg query time={avg_qtime:.2f}ms"
    )
    return out, overall


def main():
    print("=== DenseRAGMemory (embedding + cross-encoder reranking, GPU) ===")
    print()
    # baseline: top_k=5 を既存RawRAGと揃える
    run(top_k=5, candidate_k=10, use_reranker=True, label="dense+rerank top5")
    # reranker無し(密検索のみ)との比較
    run(top_k=5, candidate_k=10, use_reranker=False, label="dense only  top5")
    # 元のTF-IDF版のtop_kアブレーションと揃える
    for k in [3, 5, 8, 10]:
        run(top_k=k, candidate_k=max(k, 10), use_reranker=True, label=f"dense+rerank top{k}")


if __name__ == "__main__":
    main()
