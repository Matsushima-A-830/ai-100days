# Day 002 実行結果ログ

実行環境: このClaude Codeクラウドセッションのコンテナ内(Linux)。
`gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1)`, `clang 18.1.3`, `rustc 1.94.1`,
`cargo 1.94.1`, `python3 3.11.15`。外部APIキー・GPUは使用していない。

## 1. ビルド

```
$ gcc -O0 -g -o driver_plain driver.c rle_decode.c
$ clang -O0 -g -fsanitize=address -o driver_asan driver.c rle_decode.c
```

結果: **clangのASanは失敗した。**

```
/usr/bin/ld: cannot find /usr/lib/llvm-18/lib/clang/18/lib/linux/libclang_rt.asan_static-x86_64.a: No such file or directory
/usr/bin/ld: cannot find /usr/lib/llvm-18/lib/clang/18/lib/linux/libclang_rt.asan-x86_64.a: No such file or directory
clang: error: linker command failed with exit code 1 (use -v to see invocation)
```

このコンテナにはclang用のASanランタイムが入っていなかった。そこでgccの
ASan(`-fsanitize=address`)に切り替えたところ、こちらは問題なくビルドできた。

```
$ gcc -O0 -g -o driver_plain driver.c rle_decode.c
$ gcc -O0 -g -fsanitize=address -o driver_asan driver.c rle_decode.c
=== build ok (gcc ASan) ===
```

Rust側:

```
$ cargo build --release
   Compiling rle_decode v0.1.0 (/home/user/ai-100days/experiments/day-002/rust)
    Finished `release` profile [optimized] target(s) in 6.94s

$ cargo test
running 3 tests
test tests::decodes_valid_input_within_capacity ... ok
test tests::odd_trailing_byte_is_ignored_like_c_version ... ok
test tests::rejects_input_that_would_overflow_capacity ... ok
test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

3つの単体テストは全てpass。

## 2. 正常系での動作確認(C版 vs Rust版、1件だけ手動比較)

```
$ ./c/driver_plain 10 "03410242"
OUT_POS 5
4141414242

$ ./rust/target/release/rle_decode 10 "03410242"
OUT_POS 5
4141414242
```

出力バイト列は完全に一致した。

## 3. 異常系: out_cap=4なのに合計20バイトを要求する悪意ある入力(`14 41 00 00`)

### 3-1. C版、ASan無し(通常ビルド) — 検出されずに静かに壊れる

```
$ ./c/driver_plain 4 "144100000000"
OUT_POS 20
41414141
EXIT_CODE=0
```

`malloc(4)`で確保した4バイトのバッファに対して実際には20バイト書き込んでおり、
ヒープの他の領域を破壊しているはずだが、プログラムはクラッシュせず正常終了
(`exit code 0`)している。**これが「動いているように見えるが実際は壊れている」
という一番怖いパターン。**

### 3-2. C版、ASan有り — heap-buffer-overflowとして検出、アボート

```
$ ./c/driver_asan 4 "144100000000"
==539==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x502000000014 at pc 0x55e571e82b10 bp 0x7ffc80733180 sp 0x7ffc80733170
WRITE of size 1 at 0x502000000014 thread T0
    #0 0x55e571e82b0f in rle_decode /home/user/ai-100days/experiments/day-002/c/rle_decode.c:33
    #1 0x55e571e82876 in main /home/user/ai-100days/experiments/day-002/c/driver.c:44
    #2 0x7fbc1f02a1c9 in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #3 0x7fbc1f02a28a in __libc_start_main_impl ../csu/libc-start.c:360
    #4 0x55e571e82304 in _start (driver_asan+0x1304)

0x502000000014 is located 0 bytes after 4-byte region [0x502000000010,0x502000000014)
allocated by thread T0 here:
    #0 0x7fbc1f4fd9c7 in malloc ../../../../src/libsanitizer/asan/asan_malloc_linux.cpp:69
    #1 0x55e571e827f0 in main /home/user/ai-100days/experiments/day-002/c/driver.c:38

SUMMARY: AddressSanitizer: heap-buffer-overflow /home/user/ai-100days/experiments/day-002/c/rle_decode.c:33 in rle_decode
==539==ABORTING
EXIT_CODE=1
```

`rle_decode.c:33`(`out[out_pos] = value;`の行、境界チェックが無い箇所)が
ちょうど問題の書き込みとして特定されている。ASanをつけて初めて、
「4バイトの確保領域の直後0バイトの位置へのWRITE」として検出された。

### 3-3. Rust版 — パニックもクラッシュもせず、安全にエラーを返す

```
$ ./rust/target/release/rle_decode 4 "144100000000"
ERROR: capacity exceeded (needed >= 5, out_cap = 4) — write prevented, no memory corruption
EXIT_CODE=1
```

Rust版では`out.len() >= out_cap`の時点で書き込み自体を行わずに`Err`を返している
(`rust/src/lib.rs`の`rle_decode`関数)。exit codeは1(異常系であることを示す)だが、
これはメモリ破壊やクラッシュによるものではなく、明示的なエラーハンドリングの結果。

## 4. 差分ファジング: ランダムな正常系入力1000件

`diff_fuzz.py`(`random.Random(42)`で固定シード)で、常に合計countがout_cap以内に
収まるようなランダムな`[count, value]`ペア列を1000パターン生成し、C版(通常ビルド)
とRust版のCLI出力(`stdout`と終了コード)を比較した。

```
$ python3 diff_fuzz.py
1000 random valid cases compared, mismatches=0
```

**1000/1000ケースで完全一致(mismatches=0)。** 出力が一致しないケースは0件だった。

## まとめ(正直な評価)

- giflib本体(約3,000行)のフルスコープの書き換え・差分ファジングは6時間以内には
  再現できないため、今回は「サイズチェック漏れによるヒープ書き込み」という
  バグのクラスだけを抜き出したミニ実装(C版100行未満、Rust版60行程度)で検証した。
- 正常系1000ケースの出力一致は確認できたが、これは「ランダム生成した正常系入力」
  というかなり単純な入力空間に限られており、libFuzzer/AFLのようなカバレッジ
  ガイド付きファジングではない。あくまで「差分ファジングのごく簡易な近似」である。
- clangのASanランタイムがこの検証環境に入っておらずビルドに失敗した、という
  詰まりも実際に発生した点として記録しておく(gccのASanで回避した)。
- Rust版のRustコード自体はClaude Code(このアシスタント)が今回の対話の中で
  一から書いたものであり、Google/Geminiの実際の書き換え出力を検証したわけではない。
  あくまで「Cのメモリ安全バグをAI支援でRustに書き換えると実際に直るか」という
  手法そのものの再現実験。
