"""Grade qa_results.json / sft_results.json from several run directories with one rule,
and print a comparison table.

Usage: python grade_devices.py <label>=<dir> [<label>=<dir> ...]

Rule: an answer is correct if the expected keyword appears in the first line of the
answer (case-insensitive, word boundary). This matches the manual grading in results.md
section 2 (e.g. "Gold?" for the gold question is wrong, "The Mona Lisa" is a non-answer).
For sft_results, only the core answer is graded (first sentence); hallucinated side
remarks are not scored here.
"""
import json
import re
import sys

KEYS = {
    "Who wrote the novel Pride and Prejudice?": r"jane austen",
    "What is the chemical symbol for gold?": r"\bau\b",
    "What is the capital of Australia?": r"canberra",
    "What is the capital of Mongolia?": r"ulaanbaatar",
    "Who painted the Mona Lisa?": r"leonardo|da vinci",
    "In which year did the Berlin Wall fall?": r"\b1989\b",
    "What is the tallest mountain in the world?": r"everest",
    "Who was the first person to walk on the Moon?": r"armstrong",
}
SHORT = ["P&P", "Au", "AUS", "MNG", "Mona", "Berlin", "Everest", "Moon"]


def ok(q, text, first_sentence=False):
    t = text.split("\n")[0]
    if first_sentence:
        t = re.split(r"(?<=\.)\s", t)[0]
    return bool(re.search(KEYS[q], t, re.I))


runs = [a.split("=", 1) for a in sys.argv[1:]]
cols = [("querylm_no_search", "(A) QueryLM no search"),
        ("querylm_with_search", "(B) QueryLM search"),
        ("standard", "(C) Standard")]

print("| run | " + " | ".join(c[1] for c in cols) + " | (D) sft-search |")
print("|---|" + "---|" * (len(cols) + 1))
detail = []
for label, d in runs:
    qa = json.load(open(f"{d}/qa_results.json"))
    sft = json.load(open(f"{d}/sft_results.json"))
    cells = []
    for key, _ in cols:
        marks = [ok(r["question"], r[key]) for r in qa]
        cells.append(f"{sum(marks)}/8")
        detail.append((label, key, "".join("o" if m else "x" for m in marks)))
    marks = [ok(r["question"], r["answer"], first_sentence=True) for r in sft]
    cells.append(f"{sum(marks)}/8")
    detail.append((label, "sft_search", "".join("o" if m else "x" for m in marks)))
    print(f"| {label} | " + " | ".join(cells) + " |")

print()
print("per-question marks (order: " + ", ".join(SHORT) + ")")
for label, key, m in detail:
    print(f"  {label:10s} {key:20s} {m}")
