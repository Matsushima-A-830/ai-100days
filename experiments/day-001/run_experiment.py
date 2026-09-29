"""Small-scale concept reproduction of Writer's "Shorthand for Thought"
supertoken pipeline (https://github.com/Writer/shorthand-for-thought,
Apache-2.0), run on a self-authored substitute corpus because the paper's
real datasets (open-thoughts/OpenThoughts3-1.2M, Writer/OpenThoughts3-300K)
and tokenizers (Qwen/QwQ-32B etc.) all live on huggingface.co, which this
sandbox's network policy blocks (verified: `curl -sS https://huggingface.co`
-> CONNECT tunnel failed, response 403).

This script reuses the ACTUAL reastok library code (cloned from the repo,
Apache-2.0) for n-gram counting and merge application, and the actual
`run_bpe` merge-discovery routine from scripts/bpe_from_ngrams.py, unmodified.
Only the base tokenizer (trained locally with `tokenizers` BpeTrainer instead
of downloading Qwen/QwQ-32B's tokenizer) and the input corpus (self-authored
CoT-style reasoning traces instead of the paper's dataset) are substitutes.
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

# Path to a local clone of https://github.com/Writer/shorthand-for-thought
# (Apache-2.0). We import its actual reastok library / scripts code rather
# than reimplementing or vendoring it. Override with:
#   SHORTHAND_REPO=/path/to/shorthand-for-thought python run_experiment.py
REPO_CLONE = Path(os.environ.get("SHORTHAND_REPO", Path(__file__).parent / "shorthand-for-thought"))
sys.path.insert(0, str(REPO_CLONE))
sys.path.insert(0, str(REPO_CLONE / "scripts"))

from tokenizers import Tokenizer, models, pre_tokenizers, trainers, decoders  # noqa: E402

from reastok.ngrams import count_ngrams  # noqa: E402
from reastok.merge_apply import SuperPostTokenizer  # noqa: E402
from bpe_from_ngrams import run_bpe  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from corpus import TRAIN_TRACES, HELD_OUT_TRACES  # noqa: E402

OUT_DIR = Path(__file__).parent
NGRAM_SIZES = list(range(2, 11))  # n=2..10, same as the paper's default
MAX_COUNT_PER_SAMPLE = 10  # same cap as config/datasets.yaml project_defaults
NUM_MERGES = 200
CHECKPOINTS = [25, 50, 100, 150, 200]


def build_base_tokenizer(train_texts: list[str]) -> Tokenizer:
    """Train a small byte-level BPE tokenizer locally (no network) to stand
    in for the paper's Qwen/QwQ-32B base tokenizer."""
    tok = Tokenizer(models.BPE(unk_token=None))
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tok.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(vocab_size=3000, min_frequency=2, show_progress=False)
    tok.train_from_iterator(train_texts, trainer=trainer)
    return tok


def aggregate_ngrams(token_id_lists: list[list[int]]) -> dict[int, Counter]:
    """Mirror scripts/tokenize_ngrams.py: per-sample count cap, summed across
    the corpus, one Counter per n-gram size."""
    ngrams: dict[int, Counter] = {n: Counter() for n in NGRAM_SIZES}
    for ids in token_id_lists:
        for n in NGRAM_SIZES:
            ngrams[n].update(count_ngrams(ids, n, max_count=MAX_COUNT_PER_SAMPLE))
    return ngrams


def main():
    print("=== Step 1: train local base tokenizer (substitute for Qwen/QwQ-32B) ===")
    base_tok = build_base_tokenizer(TRAIN_TRACES)
    print(f"base vocab size: {base_tok.get_vocab_size()}")

    train_ids = [base_tok.encode(t).ids for t in TRAIN_TRACES]
    heldout_ids = [base_tok.encode(t).ids for t in HELD_OUT_TRACES]
    print(f"train samples: {len(train_ids)}, held-out samples: {len(heldout_ids)}")
    print(f"train base token counts: {[len(x) for x in train_ids]}")
    print(f"held-out base token counts: {[len(x) for x in heldout_ids]}")

    print("\n=== Step 2: count n-grams over the training traces (reastok.ngrams.count_ngrams) ===")
    ngrams = aggregate_ngrams(train_ids)
    for n in NGRAM_SIZES:
        print(f"  n={n}: {len(ngrams[n])} distinct n-grams")

    print(f"\n=== Step 3: discover {NUM_MERGES} BPE supertoken merges (scripts/bpe_from_ngrams.run_bpe, unmodified) ===")
    merges = run_bpe(ngrams, base_tok, NUM_MERGES, filter_fn=None)
    print(f"discovered {len(merges)} merges (requested {NUM_MERGES})")

    tsv_path = OUT_DIR / "bpe_merges.tsv"
    rows = ["id_a\tid_b\tid_merged\tfreq\ttok1\ttok2\tmerged"] + [
        f"{a}\t{b}\t{c}\t{freq}\t{t1}\t{t2}\t{m}" for a, b, c, freq, t1, t2, m in merges
    ]
    tsv_path.write_text("\n".join(rows) + "\n")
    print(f"wrote merge table to {tsv_path}")

    print("\n=== Step 4: apply supertokens with reastok.merge_apply.SuperPostTokenizer ===")
    super_tok = SuperPostTokenizer.from_tsv(tsv_path)

    def compress_stats(id_lists, tag):
        print(f"\n-- {tag} --")
        results = []
        for cp in CHECKPOINTS:
            st = SuperPostTokenizer.from_tsv(tsv_path, num_merges=cp)
            base_total = sum(len(ids) for ids in id_lists)
            super_total = sum(len(st.post_encode(ids)) for ids in id_lists)
            pct = 100.0 * (base_total - super_total) / base_total
            results.append(
                {
                    "num_merges": cp,
                    "base_tokens": base_total,
                    "supertoken_tokens": super_total,
                    "reduction_pct": round(pct, 2),
                }
            )
            print(
                f"  merges={cp:>4}  base={base_total:>5}  super={super_total:>5}  "
                f"reduction={pct:5.2f}%"
            )
        return results

    train_results = compress_stats(train_ids, "TRAIN (in-sample)")
    heldout_results = compress_stats(heldout_ids, "HELD-OUT (unseen traces)")

    summary = {
        "base_vocab_size": base_tok.get_vocab_size(),
        "num_train_samples": len(TRAIN_TRACES),
        "num_heldout_samples": len(HELD_OUT_TRACES),
        "ngram_sizes": NGRAM_SIZES,
        "max_count_per_sample": MAX_COUNT_PER_SAMPLE,
        "requested_merges": NUM_MERGES,
        "discovered_merges": len(merges),
        "train_results": train_results,
        "heldout_results": heldout_results,
        "example_top_merges": [
            {"freq": freq, "tok1": t1, "tok2": t2, "merged": m}
            for (_a, _b, _c, freq, t1, t2, m) in merges[:20]
        ],
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print("\nwrote summary.json")


if __name__ == "__main__":
    main()
