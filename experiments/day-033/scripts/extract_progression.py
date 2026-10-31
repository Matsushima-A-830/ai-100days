"""quantcheck (aditi-p31/quantcheck) の公開データから、
指定したOllamaモデル系列(例: "qwen2.5-coder:3b-instruct")の各量子化タグについて
HumanEval+ 通過数(15タスクのスモーク screen / 164タスクのフル実行)を抜き出す。
Ollama自体は一切呼ばない。リポジトリに同梱された評価済みJSONLを読んで集計するだけ。

使い方:
  python3 -I extract_progression.py <quantcheck_repo_root> <model_prefix>
  例: python3 -I extract_progression.py /path/to/quantcheck "llama3.2:1b-instruct"
"""
import json
import sys
from pathlib import Path

QUANT_ORDER = [
    "q2_K", "q3_K_S", "q3_K_M", "q3_K_L", "q4_0", "q4_K_S", "q4_K_M",
    "q5_K_S", "q5_K_M", "q6_K", "q8_0", "fp16",
]


def quant_key(tag: str) -> str:
    return tag.split("-")[-1]


def main() -> None:
    repo_root = Path(sys.argv[1])
    prefix = sys.argv[2]
    smoke_path = repo_root / "rerun-2026-10" / "serial" / "census_smoke_serial.jsonl"
    full164_path = repo_root / "rerun-2026-10" / "serial" / "census_full164_serial.jsonl"

    smoke_scores: dict[str, int] = {}
    with smoke_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            tag = rec.get("tag", "")
            if tag.startswith(prefix):
                smoke_scores[tag] = rec["n_pass"]

    full164_scores: dict[str, int] = {}
    with full164_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            tag = rec.get("tag", "")
            if tag.startswith(prefix):
                full164_scores[tag] = rec["n_pass"]

    rows = []
    for tag, n_pass in smoke_scores.items():
        q = quant_key(tag)
        rows.append({
            "tag": tag,
            "quant": q,
            "smoke15_pass": n_pass,
            "full164_pass": full164_scores.get(tag),
        })
    rows.sort(key=lambda r: QUANT_ORDER.index(r["quant"]) if r["quant"] in QUANT_ORDER else 99)

    print(f"{'tag':45s} {'smoke15':>8s} {'full164':>8s}")
    for r in rows:
        full = r["full164_pass"]
        print(f"{r['tag']:45s} {r['smoke15_pass']:>8d} {('' if full is None else full):>8}")


if __name__ == "__main__":
    main()
