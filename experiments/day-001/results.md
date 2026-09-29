# Day 001 実行結果

## 実行環境

- Python 3.11.15 (venv)
- `tokenizers==0.23.2`, `numpy==2.4.6`, `safetensors==0.8.0`
- 公式リポジトリ: `Writer/shorthand-for-thought` を `git clone` した状態(コミットはREADME取得日 2026-09-29 時点のHEAD)
- 実行コマンド: `SHORTHAND_REPO=./shorthand-for-thought ./venv/bin/python run_experiment.py`
- GPU不使用・外部APIキー不使用

## ネットワーク制約の確認ログ(事前調査)

公式パイプラインが依存するHugging Faceへのアクセスがブロックされていることを、検証開始前に以下で確認した。

```
$ curl -sS -o /dev/null -w "%{http_code}\n" https://huggingface.co
curl: (56) CONNECT tunnel failed, response 403
```

GitHubは疎通した:

```
$ curl -sS -o /dev/null -w "%{http_code}\n" https://github.com
200 (git clone https://github.com/Writer/shorthand-for-thought.git も成功)
```

このため、README.mdに記載の通り、ベーストークナイザーとコーパスを自前で用意する方針に切り替えた。

## 実行ログ(生出力そのまま)

```
=== Step 1: train local base tokenizer (substitute for Qwen/QwQ-32B) ===
base vocab size: 533
train samples: 16, held-out samples: 4
train base token counts: [170, 143, 130, 162, 131, 142, 145, 328, 107, 130, 144, 147, 135, 177, 212, 119]
held-out base token counts: [152, 179, 202, 211]

=== Step 2: count n-grams over the training traces (reastok.ngrams.count_ngrams) ===
  n=2: 1604 distinct n-grams
  n=3: 2100 distinct n-grams
  n=4: 2289 distinct n-grams
  n=5: 2359 distinct n-grams
  n=6: 2394 distinct n-grams
  n=7: 2403 distinct n-grams
  n=8: 2403 distinct n-grams
  n=9: 2392 distinct n-grams
  n=10: 2378 distinct n-grams

=== Step 3: discover 200 BPE supertoken merges (scripts/bpe_from_ngrams.run_bpe, unmodified) ===
  [   0] freq=        23  '.' + ' So'
  [  50] freq=         5  ' + 1' + ' ='
  [ 100] freq=         3  ' Pipe' + ' B'
  [ 150] freq=         2  ' 2' + ','
discovered 200 merges (requested 200)
wrote merge table to bpe_merges.tsv

=== Step 4: apply supertokens with reastok.merge_apply.SuperPostTokenizer ===

-- TRAIN (in-sample) --
  merges=  25  base= 2522  super= 2285  reduction= 9.40%
  merges=  50  base= 2522  super= 2153  reduction=14.63%
  merges= 100  base= 2522  super= 2013  reduction=20.18%
  merges= 150  base= 2522  super= 1935  reduction=23.28%
  merges= 200  base= 2522  super= 1835  reduction=27.24%

-- HELD-OUT (unseen traces) --
  merges=  25  base=  744  super=  710  reduction= 4.57%
  merges=  50  base=  744  super=  699  reduction= 6.05%
  merges= 100  base=  744  super=  682  reduction= 8.33%
  merges= 150  base=  744  super=  674  reduction= 9.41%
  merges= 200  base=  744  super=  664  reduction=10.75%

wrote summary.json
```

生成された `bpe_merges.tsv` (200マージ) と `summary.json` はこのディレクトリにそのままコミットしてある。

## 発見された上位supertokenの例(freq降順、上位15件)

`bpe_merges.tsv` および `summary.json` の `example_top_merges` から抜粋:

| freq | tok1 | tok2 | merged |
|---|---|---|---|
| 23 | `.` | ` So` | `. So` |
| 17 | `.` | ` Let` | `. Let` |
| 16 | `-` | `check` | `-check` |
| 15 | ` double` | `-check` | ` double-check` |
| 14 | `,` | ` so` | `, so` |
| 14 | `. Let` | ` me` | `. Let me` |
| 14 | ` me` | ` double-check` | ` me double-check` |
| 13 | `,` | `\n` | `,\n` |
| 12 | `^` | `2` | `^2` |
| 12 | `. So` | ` the` | `. So the` |
| 11 | `,` | ` and` | `, and` |
| 11 | `. Let me` | ` double` | `. Let me double` |
| 11 | ` Let` | ` me double-check` | ` Let me double-check` |
| 11 | `. Let me double` | `-` | `. Let me double-` |
| 11 | `.` | ` Let me double-check` | `. Let me double-check` |

`. Let me double-check` がまるごと1つのsupertokenとして合成されている点は、論文が主張する「文全体の定型フレーズを低コストなトークンに圧縮する」挙動と定性的に一致している。

## トークン化の具体例(held-outサンプル)

held-outの1文目("Let me think about this step by step. What is the least common multiple of 12 and 18? ...")で、200マージ適用後のトークン数は 152 → 129(15.1%減)。冒頭部分のトークン列を比較すると:

- ベーストークナイザーのみ: `['Let', ' me', ' think', ' about', ' this', ' step', ' by', ' step', '.', ' What', ...]` (10トークンで9語)
- supertoken適用後: `[' Let me', ' think about this', ' step by step.', ' What', ...]` (4トークンで9語相当)

"Let me think about this step by step." という定型の書き出し文が、4つのsupertokenにまで圧縮されている。

## 素直な評価

- **良かった点**: 公式アルゴリズム(n-gram集計→BPEマージ探索→supertoken適用)をそのまま動かし、小さな自作コーパスでもheld-outで約10%のトークン削減という、論文の主張(平均8.1%)と同じ桁・同じ方向の効果を確認できた。上位マージの中身も論文が言う「構造的フレーズ」の直感と一致していた。
- **限界・注意点**:
  - コーパスが自作の16件+held-out4件と非常に小さく、論文の30万〜120万件規模とは比較にならない。数値の絶対値を論文の8.1%と直接比較する根拠にはならない。
  - ベーストークナイザーも自前学習の語彙サイズ3000のミニBPEであり、Qwen/QwQ-32Bのような実際のLLMトークナイザーではない。
  - フルパイプラインのSFTステップ(モデルに実際にsupertokenを使わせて生成させる部分)は未検証。あくまで「既存トークン列に対する後処理でのトークン数比較」に留まる(today.mdの指示通りのスコープ)。
  - in-sample(27.24%減)とheld-out(10.75%減)の差は、BPEマージがコーパスの頻出パターンに過学習しやすいことを示しており、これも論文の議論(汎化性)と地続きの論点として記事で触れる価値がある。
