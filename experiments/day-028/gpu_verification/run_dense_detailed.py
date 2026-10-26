import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 親の day-028/ を参照

from datasets import CONVERSATIONS, QUESTIONS
from memory_methods import MutatingSummaryMemory, AppendOnlyMemory
from dense_rag_memory import DenseRAGMemory


def fuzzy_match(gold, value):
    if value is None:
        return False
    if isinstance(value, list):
        return any(fuzzy_match(gold, v) for v in value)
    g = gold.lower()
    v = str(value).lower()
    return g in v or v in g


def main():
    TOP_K = 8
    conv_by_id = {c["id"]: c for c in CONVERSATIONS}
    memories = {}
    print("=== メモリ構築 (DenseRAGMemory: embedding + cross-encoder reranking, GPU) ===")
    for conv in CONVERSATIONS:
        mut = MutatingSummaryMemory(conv["turns"])
        app = AppendOnlyMemory(conv["turns"])
        rag = DenseRAGMemory(conv["turns"], top_k=TOP_K, candidate_k=10, use_reranker=True)
        memories[conv["id"]] = {"mutating": mut, "append": app, "rag": rag}
        print(
            f"[{conv['id']}] turns={len(conv['turns'])} | "
            f"DenseRAG build={rag.build_time*1000:.3f}ms storage={rag.storage_chars}chars"
        )

    print()
    print(f"=== 質問ごとの採点 (DenseRAGMemory, top_k={TOP_K}) ===")
    results = []
    for q in QUESTIONS:
        mem = memories[q["conv_id"]]
        mut_ans = mem["mutating"].answer(q["category"], q["type"])
        app_ans = mem["append"].answer(q["category"], q["type"])
        rag_text, rag_qtime, rag_top = mem["rag"].answer(q["category"], q["type"], q["question"])

        mut_correct = fuzzy_match(q["gold"], mut_ans)
        app_correct = fuzzy_match(q["gold"], app_ans)
        rag_correct = fuzzy_match(q["gold"], rag_text)

        results.append({**q, "rag_correct": rag_correct})
        print(
            f"[{q['conv_id']}][{q['category']}][{q['type']}] Q: {q['question']}\n"
            f"  gold={q['gold']!r}\n"
            f"  Mutating -> {mut_ans!r} ({'OK' if mut_correct else 'MISS'})\n"
            f"  AppendOnly -> {app_ans!r} ({'OK' if app_correct else 'MISS'})\n"
            f"  DenseRAG retrieved turns {[t[0] for t in rag_top]} "
            f"({'OK' if rag_correct else 'MISS'}, query {rag_qtime*1000:.3f}ms)"
        )

    print()
    print("=== 集計 ===")
    for qtype in ["current", "historical"]:
        subset = [r for r in results if r["type"] == qtype]
        n = len(subset)
        acc = sum(r["rag_correct"] for r in subset) / n
        print(f"[{qtype}] n={n} | DenseRAG(top_k={TOP_K}) acc={acc:.2%}")
    overall = sum(r["rag_correct"] for r in results) / len(results)
    print(f"[overall] n={len(results)} | DenseRAG(top_k={TOP_K}) acc={overall:.2%}")

    # still-missed questions
    print()
    print("=== DenseRAGがMISSした質問 ===")
    for r in results:
        if not r["rag_correct"]:
            print(f"  [{r['conv_id']}][{r['category']}][{r['type']}] {r['question']} (gold={r['gold']!r})")


if __name__ == "__main__":
    main()
