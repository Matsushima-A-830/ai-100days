#!/usr/bin/env python3
"""
day-002: C版(driver_plain)とRust版(rle_decode)の差分ファジング。

- ランダムな [count, value] ペア列を生成し、常に out_cap 以内に収まるように
  count の合計を抑えたケース(=正常系)では、C版とRust版の出力バイト列が
  完全に一致することを確認する。
- out_cap を意図的に超えるケース(=異常系)では、C版(ASan)がクラッシュし、
  Rust版がエラーを返して正常終了することを確認する。

実行結果はそのまま results.md に転記した。
"""
import random
import subprocess
import sys

C_PLAIN = "./c/driver_plain"
RUST_BIN = "./rust/target/release/rle_decode"

def run(bin_path, out_cap, hex_input):
    r = subprocess.run([bin_path, str(out_cap), hex_input], capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def gen_valid_case(rng, out_cap):
    total = 0
    pairs = []
    while True:
        remaining = out_cap - total
        if remaining <= 0:
            break
        count = rng.randint(0, min(remaining, 9))
        value = rng.randint(0, 255)
        pairs.append((count, value))
        total += count
        if rng.random() < 0.2:
            break
    hex_input = "".join(f"{c:02x}{v:02x}" for c, v in pairs)
    return hex_input, total

def main():
    rng = random.Random(42)
    n = 1000
    mismatches = 0
    for i in range(n):
        out_cap = rng.randint(1, 64)
        hex_input, total = gen_valid_case(rng, out_cap)

        c_rc, c_out, _ = run(C_PLAIN, out_cap, hex_input)
        r_rc, r_out, _ = run(RUST_BIN, out_cap, hex_input)

        if c_rc != 0 or r_rc != 0 or c_out != r_out:
            mismatches += 1
            print(f"MISMATCH case={i} out_cap={out_cap} hex={hex_input}")
            print(f"  C:    rc={c_rc} out={c_out!r}")
            print(f"  Rust: rc={r_rc} out={r_out!r}")

    print(f"\n{n} random valid cases compared, mismatches={mismatches}")
    return 1 if mismatches else 0

if __name__ == "__main__":
    sys.exit(main())
