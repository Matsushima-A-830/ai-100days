"""Scores my hand-written model/ folder on the real ARC validation and test splits using the
Weight-Space-Programming repo's own wsp.free_model.run() (bwrap-isolated, exactly as
harness.score_free would), and separately checks it against the task's own ten given examples.

Run from the repository root with the venv active and WSP_DATA_ROOT / HF_HOME set:
    WSP_DATA_ROOT=... HF_HOME=... HF_HUB_OFFLINE=1 python score_my_model.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")
from wsp import arc, free_model

MODEL = Path("my_model")


def main():
    t0 = time.time()
    val_q, val_o, val_a = arc.load("validation")
    test_q, test_o, test_a = arc.load("test")
    print(f"loaded ARC: validation={len(val_q)} test={len(test_q)} questions ({time.time() - t0:.1f}s)")

    batches = {"validation": (val_q, val_o), "test": (test_q, test_o)}
    t1 = time.time()
    logits, size, problems = free_model.run(MODEL, batches, isolate=False, encoder=free_model.encode_of("free-arc"))
    print(f"run() took {time.time() - t1:.1f}s")
    if problems:
        print(json.dumps({"problems": problems}, indent=1))
        sys.exit(1)

    val_acc = free_model.accuracy(logits["validation"], val_a)
    test_acc = free_model.accuracy(logits["test"], test_a)
    print(json.dumps({"size": size, "validation": val_acc, "test": test_acc}, indent=1))


if __name__ == "__main__":
    main()
