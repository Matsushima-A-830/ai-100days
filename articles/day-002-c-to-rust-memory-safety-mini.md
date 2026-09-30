---
title: "GoogleのgiflibのRust書き換えをミニ再現: AIにCの脆弱コードを書き換えさせ差分ファジングで検証した"
emoji: "🦀"
type: "tech"
topics: ["rust", "c", "security", "ai", "fuzzing"]
published: false
---

## きっかけ

Googleが公開した記事によると、Gemini(AI)を使ってgiflib(約3,000行のC製GIF処理ライブラリ)を
ABI互換のRust実装に書き換え、差分ファジングで検証したという事例が紹介されていた。

- 出典: https://bughunters.google.com/blog/scaling-memory-safety
- 解説記事: https://www.infoq.com/news/2026/09/c-rust-rewrite/

移行後、公開前だったヒープ書き込みのゼロデイ(CVE-2026-26740)の影響を受けなかった、
という点が特に印象的だった。

このやり方(「Cのメモリ安全バグをAIに指摘させてRustに書き換えさせ、差分ファジングで
挙動が変わっていないか確認する」)を、giflib本体を丸ごと再現するのではなく、
個人が6時間以内に手を動かして検証できる規模まで縮小して、実際に自分の手元
(Claude Codeのセッション内)でやってみた記録。

giflib本体のコードは一切使っていない。今回書いたコードはすべて、
この検証のためにゼロから書いたオリジナルのミニ実装。

## 何を作ったか

giflibのLZWデコーダで実際に起きていた「展開後サイズのチェックを飛ばして
ヒープバッファに書き込んでしまう」というクラスのバグ(CWE-787、ヒープバッファ
オーバーフロー)を、独自の単純なRLE(Run-Length Encoding)デコーダとして再現した。

### C版(意図的にバグを入れる)

```c
/* out_cap を受け取っているが、書き込み位置 out_pos が out_cap を
 * 超えないかのチェックを一切していない(意図的なバグ) */
size_t rle_decode(const uint8_t *in, size_t in_len, uint8_t *out, size_t out_cap) {
    size_t in_pos = 0;
    size_t out_pos = 0;

    while (in_pos + 1 < in_len) {
        uint8_t count = in[in_pos];
        uint8_t value = in[in_pos + 1];
        in_pos += 2;

        for (uint8_t i = 0; i < count; i++) {
            out[out_pos] = value; /* 境界チェック無し */
            out_pos++;
        }
    }
    return out_pos;
}
```

### Rust版(Claude Codeで書き換え)

```rust
pub fn rle_decode(input: &[u8], out_cap: usize) -> Result<Vec<u8>, CapacityExceeded> {
    let mut out = Vec::with_capacity(out_cap.min(1 << 20));
    let mut pairs = input.chunks_exact(2);

    for pair in &mut pairs {
        let count = pair[0];
        let value = pair[1];
        for _ in 0..count {
            if out.len() >= out_cap {
                return Err(CapacityExceeded { needed_at_least: out.len() + 1, out_cap });
            }
            out.push(value);
        }
    }
    Ok(out)
}
```

書き込み前に必ず容量チェックを行い、超える場合は`Err`を返す。C版と違い、
そもそも境界外への書き込みが物理的に発生しない。

## 実際に動かした結果

### 1. 正常系: 出力は完全に一致

```
$ ./c/driver_plain 10 "03410242"
OUT_POS 5
4141414242

$ ./rust/target/release/rle_decode 10 "03410242"
OUT_POS 5
4141414242
```

### 2. 異常系: out_cap=4なのに合計20バイトを要求する悪意ある入力

**C版・ASan無し(通常ビルド) — クラッシュせず、静かに壊れる。これが一番怖い。**

```
$ ./c/driver_plain 4 "144100000000"
OUT_POS 20
41414141
EXIT_CODE=0
```

`malloc(4)`の4バイトバッファに実際は20バイト書き込んでおり、ヒープの他領域を
破壊しているはずだが、プログラムは正常終了している。

**C版・ASan有り — heap-buffer-overflowとして検出、アボート。**

```
$ ./c/driver_asan 4 "144100000000"
==539==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x502000000014 ...
WRITE of size 1 at 0x502000000014 thread T0
    #0 0x55e571e82b0f in rle_decode /home/.../c/rle_decode.c:33
    ...
SUMMARY: AddressSanitizer: heap-buffer-overflow .../rle_decode.c:33 in rle_decode
==539==ABORTING
EXIT_CODE=1
```

境界チェックが無い`out[out_pos] = value;`の行がそのまま特定されている。

**Rust版 — パニックもクラッシュもせず、安全にエラーを返す。**

```
$ ./rust/target/release/rle_decode 4 "144100000000"
ERROR: capacity exceeded (needed >= 5, out_cap = 4) — write prevented, no memory corruption
EXIT_CODE=1
```

exit codeは1(異常終了)だが、これはメモリ破壊やクラッシュによるものではなく、
明示的なエラーハンドリングの結果。

### 3. 差分ファジング(簡易版): ランダムな正常系入力1000件

`random.Random(42)`で固定シードのランダム生成器を使い、常に合計countが
out_cap以内に収まるような`[count, value]`ペア列を1000パターン生成し、
C版とRust版のCLI出力(stdoutと終了コード)を比較した。

```
$ python3 diff_fuzz.py
1000 random valid cases compared, mismatches=0
```

1000/1000ケースで完全一致。挙動を変えずにメモリ安全性だけを追加できていることを
(この単純な入力空間の範囲では)確認できた。

## つまづいた点(正直に書く)

`clang -fsanitize=address`でのビルドが以下のエラーで失敗した。

```
/usr/bin/ld: cannot find /usr/lib/llvm-18/lib/clang/18/lib/linux/libclang_rt.asan_static-x86_64.a: No such file or directory
```

検証環境にclang用のASanランタイムが入っていなかったため、gccの`-fsanitize=address`
に切り替えて回避した。こちらは問題なく動いた。

## 検証のスコープと限界

- giflib本体(約3,000行)を丸ごと再現したわけではない。「サイズチェック漏れに
  よるヒープ書き込み」というバグのクラスだけを抜き出したミニ実装
  (C版100行未満、Rust版60行程度)。
- 差分ファジングも、libFuzzer/AFLのようなカバレッジガイド付きファジングではなく、
  「ランダム生成した正常系入力1000件をPythonで回して出力比較する」という簡易な
  近似にとどまる。
- 今回のRustコードはClaude Code(筆者が使っているAIアシスタント)がこの検証の
  ためにゼロから書いたものであり、Google/Geminiの実際の書き換え出力そのものを
  検証したわけではない。あくまで「Cのメモリ安全バグをAI支援でRustに書き換えると
  実際に直るか」という手法自体の再現実験。

## まとめ

規模を大幅に縮小したミニ実験ではあるが、「AIに境界チェック漏れのあるCコードを
Rustへ書き換えさせ、悪意ある入力に対する挙動の差を確認する」という一連の流れは、
外部APIキーもGPUも使わずに手元で最後まで確認できた。C版は検出無しでは静かに
壊れ、ASanをつけて初めて検出でき、Rust版は最初から安全側に倒れる、という
コントラストを実際に手を動かして見られたのは収穫だった。

再現用のコード・ログは全てexperiments/day-002/以下に置いている。
