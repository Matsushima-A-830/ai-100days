"""Scale up the 8-question comparison to Natural Questions (dev split, DPR format).

Same prompts / few-shot / decoding as 02_qa_compare.py and 03_sft_variant.py, but on
the first N questions of Tevatron/wikipedia-nq `nq-dev.jsonl.gz` whose first positive
passage contains a gold answer. That passage (a 100-word Wikipedia chunk) is the
<WEB_RESPONSE> in the search conditions, i.e. an oracle retriever: the search result
always contains the answer, so (B) measures whether the model can *use* a good result.

Conditions:
  (A) QueryLM, search blocked           (C) Standard, no search
  (B) QueryLM, own query + gold passage
  (D0) sft-search, search blocked       (D) sft-search, own query + gold passage

Usage: python 04_nq_scale.py <N> <cpu|cuda> <bf16|fp32> <out.jsonl>
Grading (done here and in summarize): SQuAD-style normalization; correct if any gold
answer is a substring of the prediction (first line for base models, first sentence for
sft-search). Empty predictions are wrong.
"""
import gzip
import json
import re
import string
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

N, DEVICE, DT, OUT = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
DTYPE = {"bf16": torch.bfloat16, "fp32": torch.float32}[DT]

FEWSHOT = (
    "Question: Who wrote the novel Pride and Prejudice?\nAnswer: Jane Austen\n\n"
    "Question: What is the chemical symbol for gold?\nAnswer: Au\n\n"
)
FEWSHOT_SEARCH = (
    "Question: Who wrote the novel Pride and Prejudice?\n"
    "<WEB_QUERY>Pride and Prejudice author</WEB_QUERY> "
    "<WEB_RESPONSE>Pride and Prejudice is an 1813 novel of manners written by Jane Austen.</WEB_RESPONSE>\n"
    "Answer: Jane Austen\n\n"
    "Question: What is the chemical symbol for gold?\n"
    "<WEB_QUERY>gold chemical symbol</WEB_QUERY> "
    "<WEB_RESPONSE>Gold is a chemical element with the symbol Au and atomic number 79.</WEB_RESPONSE>\n"
    "Answer: Au\n\n"
)


def norm(s):
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def hit(pred, answers):
    p = norm(pred)
    return bool(p) and any(norm(a) and norm(a) in p for a in answers)


def first_sentence(t):
    return re.split(r"(?<=[.!?])\s", t.strip().split("\n")[0])[0]


def load_items(n):
    items = []
    with gzip.open("data/nq-dev.jsonl.gz", "rt") as f:
        for line in f:
            d = json.loads(line)
            if not d["positive_passages"]:
                continue
            p = d["positive_passages"][0]
            passage = p["text"].replace("\n", " ").strip()
            if not hit(passage, d["answers"]):
                continue
            q = d["query"].strip()
            q = q[0].upper() + q[1:] + ("" if q.endswith("?") else "?")
            items.append({"id": d["query_id"], "question": q, "answers": d["answers"],
                          "passage": passage, "passage_title": p["title"]})
            if len(items) >= n:
                break
    return items


def load(repo):
    tok = AutoTokenizer.from_pretrained(repo)
    model = AutoModelForCausalLM.from_pretrained(repo, dtype=DTYPE).to(DEVICE).eval()
    return tok, model


@torch.no_grad()
def gen(model, tok, text, max_new_tokens, stop_id=None, block_ids=None):
    x = tok(text, add_special_tokens=False, return_tensors="pt").to(DEVICE)
    kw = {} if not block_ids else {"bad_words_ids": [[i] for i in block_ids]}
    out = model.generate(**x, max_new_tokens=max_new_tokens, do_sample=False,
                         eos_token_id=stop_id, pad_token_id=tok.eos_token_id, **kw)
    return tok.decode(out[0, x.input_ids.shape[1]:], skip_special_tokens=True)


def main():
    items = load_items(N)
    print(f"[04] n={len(items)} device={DEVICE} dtype={DT} torch={torch.__version__}"
          + (f" gpu={torch.cuda.get_device_name(0)}" if DEVICE == "cuda" else ""), flush=True)
    tq, mq = load("models/querylm-wiki-360m")
    ts, ms = load("models/standard-wiki-360m")
    tf, mf = load("models/querylm-wiki-360m-sft-search")
    QO, QC = tq.convert_tokens_to_ids("<WEB_QUERY>"), tq.convert_tokens_to_ids("</WEB_QUERY>")
    FO, FC = tf.convert_tokens_to_ids("<WEB_QUERY>"), tf.convert_tokens_to_ids("</WEB_QUERY>")

    t0 = time.time()
    with open(OUT, "w") as fo:
        for i, it in enumerate(items):
            q, P, ans = it["question"], it["passage"], it["answers"]
            r = dict(it)
            r["A"] = gen(mq, tq, FEWSHOT + f"Question: {q}\nAnswer:", 16, block_ids=[QO]).split("\n")[0].strip()
            pb = FEWSHOT_SEARCH + f"Question: {q}\n"
            r["B_query"] = gen(mq, tq, pb + "<WEB_QUERY>", 24, stop_id=QC).strip()
            blk = f"<WEB_QUERY>{r['B_query']}</WEB_QUERY> <WEB_RESPONSE>{P}</WEB_RESPONSE>"
            r["B"] = gen(mq, tq, pb + blk + "\nAnswer:", 16, block_ids=[QO]).split("\n")[0].strip()
            r["C"] = gen(ms, ts, FEWSHOT + f"Question: {q}\nAnswer:", 16).split("\n")[0].strip()
            pd = f"User: {q}\n\nAssistant: "
            r["D0"] = gen(mf, tf, pd, 64, block_ids=[FO]).split("\n\nUser:")[0].strip()
            r["D_query"] = gen(mf, tf, pd + "<WEB_QUERY>", 24, stop_id=FC).strip()
            blk = f"<WEB_QUERY>{r['D_query']}</WEB_QUERY> <WEB_RESPONSE>{P}</WEB_RESPONSE>"
            r["D"] = gen(mf, tf, pd + blk, 64, block_ids=[FO]).split("\n\nUser:")[0].strip()
            r["hit"] = {k: hit(r[k], ans) for k in ("A", "B", "C")}
            r["hit"].update({k: hit(first_sentence(r[k]), ans) for k in ("D0", "D")})
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
            fo.flush()
            if (i + 1) % 25 == 0:
                print(f"  {i + 1}/{len(items)}  {time.time() - t0:.0f}s", flush=True)
    print(f"[04] done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
