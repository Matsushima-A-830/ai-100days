# Day 002: 小さなCコードをAI支援でRustに書き換え、差分ファジングで検証する

## これは何か

GoogleがGeminiを使ってgiflib(約3,000行のC製GIFライブラリ)をRustに書き換え、
差分ファジングで検証した事例
(出典: https://bughunters.google.com/blog/scaling-memory-safety 、
解説: https://www.infoq.com/news/2026/09/c-rust-rewrite/)
のスコープを個人が6時間以内に再現できる規模まで縮小したミニ実験。

giflibのLZWデコーダで実際に問題になった「展開後のサイズチェックを
飛ばしてヒープバッファに書き込んでしまう」というクラスのバグ
(CWE-787, ヒープバッファオーバーフロー)を、独自の単純なRLE(Run-Length
Encoding)デコーダとして再現し、

1. C版(意図的にバグを入れる)
2. Claude Code(このアシスタント)がAI支援でRustに書き換えた版(安全に修正)

の2つを実装し、
- 正常系の入力1000ケースで両者の出力バイト列が完全一致すること
- 異常系の入力(出力バッファを超えるサイズを要求する悪意ある入力)で
  C版がAddressSanitizer(ASan)経由でヒープバッファオーバーフローとして
  検出されること、ASan無しでは検出されずに静かにメモリ破壊が起きること、
  Rust版はパニックもクラッシュもせずエラーを返すこと

を実際に手元で実行して確認した。

外部APIキー・GPUは不要。Claude Code自身の機能(コード生成・実行)のみで検証。

## 対象コードのライセンス・出典について

再現に使ったコード(`c/rle_decode.c`, `rust/src/lib.rs` 等)は本実験のために
ゼロから書いたオリジナルのミニ実装であり、giflib本体のコードは一切使用・
転載していない。giflibで実際に起きた問題のクラス(サイズチェック漏れに
よるヒープ書き込み)を模しただけ。giflib自体はMITライセンス。

## ディレクトリ構成

```
experiments/day-002/
├── README.md          (このファイル)
├── results.md          実行ログ・結果
├── diff_fuzz.py         差分ファジングスクリプト
├── c/
│   ├── rle_decode.c     意図的にバグを入れたC版デコーダ
│   └── driver.c          CLIラッパー
└── rust/                 Rust版(cargo new --bin rle_decode)
    ├── Cargo.toml
    └── src/
        ├── lib.rs          Claude Codeで書き換えた安全なRust実装 + 単体テスト
        └── main.rs         CLIラッパー(C版と同じ入出力形式)
```

## 再現手順

前提: gcc, clang(または gcc の ASan で十分), rustc/cargo, python3 が入っていること。

```bash
cd experiments/day-002

# 1. C版をビルド(通常版とASan版)
cd c
gcc -O0 -g -o driver_plain driver.c rle_decode.c
gcc -O0 -g -fsanitize=address -o driver_asan driver.c rle_decode.c
cd ..

# 2. Rust版をビルド + 単体テスト実行
cd rust
cargo build --release
cargo test
cd ..

# 3. 正常系: C版とRust版の出力を1回だけ手で比較
./c/driver_plain 10 "03410242"          # -> OUT_POS 5 / 4141414242
./rust/target/release/rle_decode 10 "03410242"   # -> 同じ出力になるはず

# 4. 異常系: out_cap=4なのに合計20バイト要求する悪意ある入力
./c/driver_plain 4 "144100000000"        # ASan無し: クラッシュせず"OUT_POS 20"と出て静かに壊れる
./c/driver_asan  4 "144100000000"        # ASan有り: heap-buffer-overflowとして検出されアボート
./rust/target/release/rle_decode 4 "144100000000"  # クラッシュせず"ERROR: capacity exceeded ..."で正常終了(exit 1)

# 5. 差分ファジング: ランダムな正常系入力1000件でC版とRust版の出力が完全一致するか確認
python3 diff_fuzz.py
```

## 実際に確認した結果

`results.md` に実行ログをそのまま記録した。要約:

- 正常系1000ケース: C版・Rust版の出力バイト列は全て一致(mismatches=0)。
- 異常系(悪意ある入力、out_cap超過): C版はASan無しだと静かにヒープ破壊(検出されない)、
  ASan有りだと`heap-buffer-overflow`として検出されアボート。Rust版はどちらの場合も
  クラッシュせず`Err`を返してプロセスは正常終了(exit code 1)。
