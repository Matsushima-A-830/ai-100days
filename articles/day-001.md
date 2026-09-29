---
title: "LLMの『Let me double-check』を1トークンに圧縮する—Shorthand for Thoughtを小さく動かしてみた"
emoji: "🧵"
type: "tech"
topics: ["ai", "llm", "tokenizer", "nlp", "arxiv"]
published: true
---

## この記事について

海外AIネタを毎日1つ実際に検証して発信する個人チャレンジのDay 001。今回選んだのは、COLM 2026に採択された論文 [Shorthand for Thought: Compressing LLM Reasoning with Learned Supertokens](https://arxiv.org/abs/2604.26355) と、その公開コード [Writer/shorthand-for-thought](https://github.com/Writer/shorthand-for-thought)(Apache-2.0)。

「LLMの思考(reasoning)は `Wait,` `So,` `Let me double-check` のような定型フレーズを大量に含んでいて、そこにトークンを無駄遣いしている。だったらそういう定型フレーズをBPEで1つの『supertoken』にまとめてモデルに学習させれば、精度を落とさず思考の長さを平均8.1%短縮できる」という論文で、3モデルファミリー×5つの数学ベンチマークで検証済み・モデル非依存とされている。

筆者はこの論文をそのまま丸ごと再現したわけではない。**実際に手を動かして分かった「できたこと」と「できなかったこと」を両方正直に書く**のがこの連載のルールなので、まずその線引きから書く。

## やったこと・やらなかったこと

公式パイプラインは以下の4ステップで構成されている(READMEより):

1. 推論トレースをトークナイズしてn-gram頻度を数える
2. BPEでマージテーブル(=supertoken候補)を構築する
3. 自己完結型のトークナイザーアーティファクトを作る
4. supertokenでエンコードする

このうち1〜4のアルゴリズム部分(`reastok.ngrams.count_ngrams`、`scripts/bpe_from_ngrams.run_bpe`、`reastok.merge_apply.SuperPostTokenizer`)は**公式コードをそのまま**呼び出した。自分で再実装はしていない。

一方で、公式パイプラインが前提にしている

- データセット(`open-thoughts/OpenThoughts3-1.2M` など)
- ベーストークナイザー(`Qwen/QwQ-32B` など)

はどちらもHugging Face上にあり、今回の実行環境ではネットワークポリシー上 `huggingface.co` へのアクセスがブロックされていた(`curl https://huggingface.co` → `403`)。GitHubへのアクセスは通ったので、リポジトリのクローンはできたが、データセットとトークナイザーのダウンロードはできなかった。

そこで、**規模を大きく落とした概念実証**に切り替えた。

- コーパス: 筆者が書いた、論文が扱うような数学系CoT(chain-of-thought)風の解説文を16件(訓練用)+4件(held-out用)自作。実際のLLM出力ではない。
- ベーストークナイザー: `tokenizers` ライブラリの `BpeTrainer` で、このコーパス上に語彙サイズ3000の小さなbyte-level BPEトークナイザーを自前で学習(Qwen/QwQ-32Bの代替)。

つまり「公式アルゴリズムを、小さな自作データで動かしたらどうなるか」という実験であり、**論文の8.1%という数値の再現ではない**。この点は誤解しないでほしい。

## 実行環境

- Python 3.11.15、CPUのみ、GPU不要、外部APIキー不要
- 依存: `tokenizers==0.23.2`, `numpy==2.4.6`, `safetensors==0.8.0`

## 手順

```bash
python3 -m venv venv
./venv/bin/pip install tokenizers numpy safetensors
git clone https://github.com/Writer/shorthand-for-thought.git shorthand-for-thought
SHORTHAND_REPO=./shorthand-for-thought ./venv/bin/python run_experiment.py
```

スクリプトの中身は大まかに以下の通り(全文は[experiments/day-001/run_experiment.py](https://github.com/Matsushima-A-830/ai-100days/blob/main/experiments/day-001/run_experiment.py)):

```python
from reastok.ngrams import count_ngrams
from reastok.merge_apply import SuperPostTokenizer
from bpe_from_ngrams import run_bpe  # 公式スクリプトの関数をそのまま import

# 1. 自前ベーストークナイザーで訓練データをエンコード
train_ids = [base_tok.encode(t).ids for t in TRAIN_TRACES]

# 2. n-gram集計(n=2〜10, サンプルあたり上限10 = 公式デフォルトと同じ)
ngrams = aggregate_ngrams(train_ids)

# 3. BPEマージ探索(公式コードそのまま、200マージ)
merges = run_bpe(ngrams, base_tok, 200, filter_fn=None)

# 4. supertoken適用でトークン数を比較
super_tok = SuperPostTokenizer.from_tsv(tsv_path, num_merges=200)
```

## 結果

実行ログの生出力・詳細な考察は [results.md](https://github.com/Matsushima-A-830/ai-100days/blob/main/experiments/day-001/results.md) にそのまま置いてある。ここでは要点だけ。

### トークン数の削減率

held-out(訓練に使っていない4件)で、マージ数を増やすほど削減率が伸びた。

| マージ数 | ベーストークン数 | supertoken適用後 | 削減率 |
|---|---|---|---|
| 25 | 744 | 710 | 4.57% |
| 50 | 744 | 699 | 6.05% |
| 100 | 744 | 682 | 8.33% |
| 150 | 744 | 674 | 9.41% |
| 200 | 744 | 664 | **10.75%** |

論文の headline 数値(平均8.1%)と、桁・方向性が一致する結果になった。ただし前述の通りコーパス規模がまったく違うので、この一致は「アルゴリズムがちゃんと機能している」ことの確認であって、数値そのものの再現ではない。

参考までに訓練データ(in-sample)では27.24%まで削減されており、held-outとの差(10.75% vs 27.24%)は「BPEマージがコーパスの頻出パターンに最適化されるので、未知データでは効果が薄まる」という、ある意味で予想通りの過学習的挙動だった。

### 実際にどんなsupertokenが見つかったか

発見された上位マージ(頻度順)を見ると、狙い通り「構造的な定型フレーズ」が1トークン化されているのが分かる。

| freq | tok1 | tok2 | merged |
|---|---|---|---|
| 23 | `.` | ` So` | `. So` |
| 16 | `-` | `check` | `-check` |
| 15 | ` double` | `-check` | ` double-check` |
| 14 | `. Let` | ` me` | `. Let me` |
| 14 | ` me` | ` double-check` | ` me double-check` |
| 11 | `.` | ` Let me double-check` | `. Let me double-check` |

最後の行は、マージが連鎖して `. Let me double-check` という**文全体がまるごと1つのトークンID**になっている例。実際にheld-outの1文でトークン列を比較すると:

- ベーストークナイザーのみ: `['Let', ' me', ' think', ' about', ' this', ' step', ' by', ' step', '.', ' What', ...]`(冒頭9語で10トークン)
- supertoken適用後: `[' Let me', ' think about this', ' step by step.', ' What', ...]`(同じ9語で4トークン)

"Let me think about this step by step." という、LLMの思考トレースで死ぬほど見かける書き出し文が、4つのsupertokenに圧縮されている。これは体感としてかなり分かりやすい。

## 分かったこと・次にやるなら

- **アルゴリズムの核心(頻出フレーズをBPEでsupertoken化してトークン数を削る)は、小さな自作データでもちゃんと機能する**ことを、公式コードをそのまま動かして確認できた。
- 一方で、論文の本体である「SFTでモデルにsupertokenを実際に使わせて生成させ、精度を落とさず思考が短くなるか」という部分は今回まったく検証できていない。これはGPUと学習パイプラインが必要で、6時間の個人検証の範囲を超える。
- もし次にやるなら、実際のHugging Face上の小型モデル・小型データセットにアクセスできる環境で、同じ `run_experiment.py` の `SHORTHAND_REPO` を公式の `config/datasets.yaml` の設定に差し替えて、本物の推論トレースでの削減率を見てみたい。

## 出典

- 論文: [arXiv:2604.26355 — Shorthand for Thought: Compressing LLM Reasoning with Learned Supertokens](https://arxiv.org/abs/2604.26355)
- コード: [Writer/shorthand-for-thought](https://github.com/Writer/shorthand-for-thought)(Apache License 2.0)
- 検証コード・ログ全文: [experiments/day-001/](https://github.com/Matsushima-A-830/ai-100days/tree/main/experiments/day-001)(このリポジトリ)
