"""
Day 028 メイン実験スクリプト。

3つの架空の会話ログに対して、
  1) MutatingSummaryMemory (要約・変異型 = UPDATE/DELETE相当)
  2) AppendOnlyMemory (追記のみ、削除・上書きなし)
  3) RawRAGMemory (生ログ + 自作TF-IDF検索、要約なし)
を構築し、同じ質問セット(QUESTIONS, datasets.py)に対する正答率・構築コスト・
検索コストを比較する。

実行方法:
    python3 run_experiment.py
"""
from datasets import CONVERSATIONS, QUESTIONS
from memory_methods import MutatingSummaryMemory, AppendOnlyMemory, RawRAGMemory


def fuzzy_match(gold, value):
    if value is None:
        return False
    if isinstance(value, list):
        return any(fuzzy_match(gold, v) for v in value)
    g = gold.lower()
    v = str(value).lower()
    return g in v or v in g


def main():
    conv_by_id = {c["id"]: c for c in CONVERSATIONS}
    memories = {}
    print("=== メモリ構築 ===")
    for conv in CONVERSATIONS:
        mut = MutatingSummaryMemory(conv["turns"])
        app = AppendOnlyMemory(conv["turns"])
        rag = RawRAGMemory(conv["turns"], top_k=5)
        memories[conv["id"]] = {"mutating": mut, "append": app, "rag": rag}
        print(
            f"[{conv['id']}] turns={len(conv['turns'])} | "
            f"Mutating build={mut.build_time*1000:.3f}ms storage={mut.storage_chars}chars | "
            f"AppendOnly build={app.build_time*1000:.3f}ms storage={app.storage_chars}chars | "
            f"RawRAG build={rag.build_time*1000:.3f}ms storage={rag.storage_chars}chars"
        )

    print()
    print("=== 質問ごとの採点 ===")
    results = []
    for q in QUESTIONS:
        mem = memories[q["conv_id"]]
        mut_ans = mem["mutating"].answer(q["category"], q["type"])
        app_ans = mem["append"].answer(q["category"], q["type"])
        rag_text, rag_qtime, rag_top = mem["rag"].answer(q["category"], q["type"], q["question"])

        mut_correct = fuzzy_match(q["gold"], mut_ans)
        app_correct = fuzzy_match(q["gold"], app_ans)
        rag_correct = fuzzy_match(q["gold"], rag_text)

        results.append({
            **q,
            "mut_ans": mut_ans, "mut_correct": mut_correct,
            "app_ans": app_ans, "app_correct": app_correct,
            "rag_correct": rag_correct, "rag_qtime_ms": rag_qtime * 1000,
            "rag_top_turns": [t[0] for t in rag_top],
        })
        print(
            f"[{q['conv_id']}][{q['category']}][{q['type']}] Q: {q['question']}\n"
            f"  gold={q['gold']!r}\n"
            f"  Mutating -> {mut_ans!r} ({'OK' if mut_correct else 'MISS'})\n"
            f"  AppendOnly -> {app_ans!r} ({'OK' if app_correct else 'MISS'})\n"
            f"  RawRAG retrieved turns {[t[0] for t in rag_top]} "
            f"({'OK' if rag_correct else 'MISS'}, query {rag_qtime*1000:.3f}ms)"
        )

    print()
    print("=== 集計 ===")
    for qtype in ["current", "historical"]:
        subset = [r for r in results if r["type"] == qtype]
        n = len(subset)
        mut_acc = sum(r["mut_correct"] for r in subset) / n
        app_acc = sum(r["app_correct"] for r in subset) / n
        rag_acc = sum(r["rag_correct"] for r in subset) / n
        print(
            f"[{qtype}] n={n} | Mutating acc={mut_acc:.2%} | "
            f"AppendOnly acc={app_acc:.2%} | RawRAG acc={rag_acc:.2%}"
        )

    print()
    print("=== 構築コスト・ストレージサイズ合計 ===")
    total_mut_build = sum(m["mutating"].build_time for m in memories.values())
    total_app_build = sum(m["append"].build_time for m in memories.values())
    total_rag_build = sum(m["rag"].build_time for m in memories.values())
    total_mut_storage = sum(m["mutating"].storage_chars for m in memories.values())
    total_app_storage = sum(m["append"].storage_chars for m in memories.values())
    total_rag_storage = sum(m["rag"].storage_chars for m in memories.values())
    print(
        f"Mutating: build={total_mut_build*1000:.3f}ms storage={total_mut_storage}chars\n"
        f"AppendOnly: build={total_app_build*1000:.3f}ms storage={total_app_storage}chars\n"
        f"RawRAG: build={total_rag_build*1000:.3f}ms storage={total_rag_storage}chars"
    )
    avg_rag_qtime = sum(r["rag_qtime_ms"] for r in results) / len(results)
    print(f"RawRAG average query time: {avg_rag_qtime:.3f}ms (n={len(results)} queries)")


if __name__ == "__main__":
    main()
