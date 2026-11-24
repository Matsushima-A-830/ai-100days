"""Summarize nq_scale_results.jsonl from 04_nq_scale.py.

Prints accuracy per condition with a 95% Wilson interval, the A->B flip counts
(search helped / hurt), McNemar exact p-values for A vs C and A vs B, how often the
gold answer string appears in the model's own query, and how often a base model just
echoes the question back.
"""
import json
import math
import sys
from math import comb

rows = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else "nq_scale_results.jsonl")]
n = len(rows)


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


def mcnemar(b, c):
    m = b + c
    if m == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(m, i) for i in range(k + 1)) / 2 ** m)


names = {"A": "(A) QueryLM, no search", "B": "(B) QueryLM, own query + gold passage",
         "C": "(C) Standard, no search", "D0": "(D0) sft-search, no search",
         "D": "(D) sft-search, own query + gold passage"}
print(f"n = {n} questions (NQ dev, DPR positive passage contains the answer)\n")
print("| condition | correct | accuracy | 95% CI |")
print("|---|---|---|---|")
for k, name in names.items():
    c = sum(r["hit"][k] for r in rows)
    lo, hi = wilson(c, n)
    print(f"| {name} | {c}/{n} | {100 * c / n:.1f}% | {100 * lo:.1f}-{100 * hi:.1f}% |")


def pair(x, y):
    xo_yx = sum(r["hit"][x] and not r["hit"][y] for r in rows)
    xx_yo = sum(not r["hit"][x] and r["hit"][y] for r in rows)
    return xo_yx, xx_yo


print()
for x, y, label in [("A", "C", "QueryLM vs Standard (no search)"),
                    ("A", "B", "QueryLM: no search -> search"),
                    ("D0", "D", "sft-search: no search -> search")]:
    b, c = pair(x, y)
    print(f"{label}: only {x} correct = {b}, only {y} correct = {c}, McNemar exact p = {mcnemar(b, c):.3g}")

print()
for k in ("A", "B", "C"):
    echo = sum(bool(r[k].lower().rstrip("?").strip()) and r[k].lower().rstrip("?").strip() in r["question"].lower() for r in rows)
    empty = sum(not r[k].strip() for r in rows)
    print(f"{k}: empty answers = {empty}, answer is a substring of the question = {echo}")


def norm(s):
    import re, string
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


for k in ("B_query", "D_query"):
    leak = sum(any(norm(a) and norm(a) in norm(r[k]) for a in r["answers"]) for r in rows)
    shot = sum(any(w in r[k].lower() for w in ("jane austen", "pride and prejudice", " au ", "gold"))
               or r[k].lower().startswith("au ") for r in rows)
    print(f"{k}: contains gold answer = {leak}, contains few-shot words (Jane Austen/Pride and Prejudice/Au/gold) = {shot}")
