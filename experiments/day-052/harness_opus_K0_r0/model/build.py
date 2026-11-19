"""Turn the hand-written knowledge base (kb/*.txt), word families and stop words into the weights.

Weights:
  stem_of    (V+2,) int64   word id -> concept (stem) id; 0 for padding, unknown words and stop words
  idf        (C,)   float   inverse document frequency of each concept over the knowledge-base sentences
  sent_*     (N, C) sparse  sentence x concept incidence, each row scaled by 1 / len(sentence)^LEN_POW
  assoc_*    (C, C) sparse  positive pointwise mutual information of concepts co-occurring in a sentence
             (sparse matrices are kept as index and value tensors and assembled in arch.py)
  neg_word   (V+2,) float   1 for words that make a question negative on their own (except, least, ...)
  which_word (V+2,) float   1 for which/what: a "not" within six words after them makes the question negative
  not_word   (V+2,) float   1 for "not"
  scalars: hyper-parameters chosen by hand
"""
import glob
import math
import re
from collections import Counter

import numpy as np
import torch

from textproc import Stemmer, load_families, words

LEN_POW = 0.5
PHRASE_W = 0.5  # idf multiplier of phrase concepts
CROSS_POLARITY = 0.5  # support of a negated sentence for a plain option, and of a plain sentence for a negated option
NEGATION = {"not", "no", "cannot", "never", "without", "neither", "nor", "don't", "doesn't", "isn't", "aren't",
            "can't", "won't", "unable", "none"}


def read_list(path):
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0]
        out += words(line)
    return out


def kb_sentences():
    sents = []
    for f in sorted(glob.glob("kb/*.txt")):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("="):
                # "= category words | item one, item two" -> one sentence per item: "item one category words"
                head, items = line[1:].split("|", 1)
                for it in items.split(","):
                    if it.strip():
                        sents.append(it.strip() + " " + head.strip())
            else:
                # clauses joined by ";" are also kept as separate facts (they often contrast two things)
                sents.append(line)
                parts = [part.strip() for part in re.split(r";|, but | but |, while ", line) if part.strip()]
                if len(parts) > 1:
                    sents += parts
    return sents


def build():
    vocab = [ln.strip() for ln in open("vocab.txt", encoding="utf-8")]
    stem = Stemmer(load_families("families.txt"))
    stop = set(read_list("stopwords.txt"))
    sents = kb_sentences()

    # concepts: stems of all non-stop vocabulary words
    cid = {}
    stem_of = np.zeros(len(vocab) + 2, dtype=np.int64)
    for i, wd in enumerate(vocab):
        if wd in stop:
            continue
        s = stem(wd)
        if s in stop or s.lstrip("#") in stop:
            continue
        stem_of[i + 2] = cid.setdefault(s, len(cid) + 1)
    C = len(cid) + 1

    # sentence incidence, over word concepts and phrase concepts (adjacent content-word pairs of the knowledge base)
    seqs = []
    for text in sents:
        seq = []
        for wd in words(text):
            if wd in stop:
                continue
            c = cid.get(stem(wd))
            if c:
                seq.append(c)
        seqs.append(seq)
    keys = sorted({a * C + b for seq in seqs for a, b in zip(seq, seq[1:]) if a != b})
    key_id = {k: C + i for i, k in enumerate(keys)}
    CB = C + len(keys)
    df = Counter()
    sent_sets = []
    for seq in seqs:
        cs = set(seq) | {key_id[a * C + b] for a, b in zip(seq, seq[1:]) if a != b}
        sent_sets.append(cs)
        df.update(cs)
    N = len(sents)
    idf = np.zeros(CB, dtype=np.float32)
    for c, d in df.items():
        idf[c] = math.log((N + 1) / (d + 0.5)) * (PHRASE_W if c >= C else 1.0)
    rows, cols, vals = [], [], []
    for si, cs in enumerate(sent_sets):
        n_words = sum(1 for c in cs if c < C)
        if not n_words:
            continue
        scale = 1.0 / (n_words ** LEN_POW)
        for c in cs:
            rows.append(si)
            cols.append(c)
            vals.append(scale)
    sent = torch.sparse_coo_tensor(torch.tensor([rows, cols]), torch.tensor(vals, dtype=torch.float32), (N, CB)).coalesce()
    sent_idx, sent_val = sent.indices(), sent.values()
    sent_neg = torch.tensor([1.0 if NEGATION & set(words(t)) else 0.0 for t in sents])

    # concept association (PPMI over sentence co-occurrence)
    pair = Counter()
    for cs in sent_sets:
        cl = sorted(c for c in cs if c < C)
        if len(cl) > 40:
            continue
        for a in range(len(cl)):
            for b in range(a + 1, len(cl)):
                pair[(cl[a], cl[b])] += 1
    ar, ac, av = [], [], []
    for (a, b), n_ab in pair.items():
        pmi = math.log(n_ab * N / (df[a] * df[b]))
        if pmi <= 0:
            continue
        # damp pairs seen once with rare words (pmi grows without bound for them)
        v = pmi * (n_ab / (n_ab + 1.0))
        ar += [a, b]
        ac += [b, a]
        av += [v, v]
    assoc = torch.sparse_coo_tensor(torch.tensor([ar, ac]), torch.tensor(av, dtype=torch.float32), (CB, CB)).coalesce()
    assoc_idx, assoc_val = assoc.indices(), assoc.values()

    index = {wd: i + 2 for i, wd in enumerate(vocab)}

    def flags(ws):
        f = torch.zeros(len(vocab) + 2)
        for x in ws:
            if x in index:
                f[index[x]] = 1.0
        return f

    keep = torch.ones(CB)
    keep[0] = 0
    return {
        "stem_of": torch.from_numpy(stem_of),
        "phrase_keys": torch.tensor(keys + [CB * CB], dtype=torch.int64),  # sorted; sentinel at the end
        "phrase_base": torch.tensor(C, dtype=torch.int64),
        "n_words": torch.tensor(C, dtype=torch.int64),
        "idf": torch.from_numpy(idf),
        "keep": keep,
        # sparse matrices are stored as (2, nnz) indices and (nnz,) values; arch.py assembles them
        "sent_idx": sent_idx,
        "sent_val": sent_val,
        "sent_neg": sent_neg,
        "neg_option_word": flags(sorted(NEGATION)),
        "assoc_idx": assoc_idx,
        "assoc_val": assoc_val,
        "neg_word": flags(["except"]),
        "least_word": flags(["least"]),
        "likely_word": flags(["likely", "probably", "affected", "useful", "helpful", "important", "effective", "able",
                              "accurate", "reliable", "appropriate", "related", "similar", "beneficial"]),
        "which_word": flags(["which", "what"]),
        "not_word": flags(["not"]),
        "len_word": flags([]) + 1.0,
        "hp": torch.tensor([
            2.0,    # 0 pos_boost: extra weight of the last words of the question
            10.0,   # 1 pos_scale: in words
            1.0,    # 2 weight of the retrieval score
            0.02,   # 3 weight of the association score
            0.002,  # 4 weight of option length (tie-break)
            0.8,    # 5 strength of negation flip
            0.3,    # 6 weight of second-best sentence
            CROSS_POLARITY,  # 7
            0.4,    # 8 exponent of the option-length normalization
            1.0,    # 9 exponent of the question coverage of a sentence
            0.9,    # 10 how much option words that also occur in the question are discounted
        ]),
    }
