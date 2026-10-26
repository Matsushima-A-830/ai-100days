"""
Day 028 追加検証: RawRAGMemoryの検索精度が低く出た原因を切り分けるアブレーション。

run_experiment.py のベースライン実装(発言者ラベル"Aki: "を含めてトークン化、
語幹処理なし)に対して、
  - 発言者ラベルを除いてトークン化する(名前がノイズになっていないか)
  - 簡易な語幹処理(stem)を入れる("job" と "jobs" のような表記差を吸収できるか)
を1つずつオンにして、正答率がどう変わるかを比較する。

実行方法:
    python3 ablation_rag.py
"""
from datasets import CONVERSATIONS, QUESTIONS
from memory_methods import RawRAGMemory


def fuzzy_match(gold, text):
    return gold.lower() in text.lower()


def evaluate(include_speaker, stem, top_k=5):
    memories = {
        c["id"]: RawRAGMemory(c["turns"], top_k=top_k, include_speaker=include_speaker, stem=stem)
        for c in CONVERSATIONS
    }
    correct_by_type = {"current": [], "historical": []}
    for q in QUESTIONS:
        rag = memories[q["conv_id"]]
        text, _, _ = rag.answer(q["category"], q["type"], q["question"])
        correct_by_type[q["type"]].append(fuzzy_match(q["gold"], text))
    return {
        qtype: sum(vals) / len(vals) for qtype, vals in correct_by_type.items()
    }


if __name__ == "__main__":
    configs = [
        ("baseline (speaker label入り, stemなし)", True, False),
        ("speaker label除去", False, False),
        ("speaker label除去 + 簡易stem", False, True),
        ("speaker label入り + 簡易stemのみ", True, True),
    ]
    print("=== RawRAG 検索方式のアブレーション ===")
    for label, include_speaker, stem in configs:
        acc = evaluate(include_speaker, stem)
        print(
            f"[{label}] current acc={acc['current']:.2%} | historical acc={acc['historical']:.2%}"
        )
