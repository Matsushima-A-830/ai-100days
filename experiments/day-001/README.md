# Day 001: Shorthand for Thought — supertokenで推論トークンを削減できるか小規模検証

出典:
- 論文: [Shorthand for Thought: Compressing LLM Reasoning with Learned Supertokens](https://arxiv.org/abs/2604.26355) (COLM 2026採択)
- コード: [Writer/shorthand-for-thought](https://github.com/Writer/shorthand-for-thought) (Apache-2.0)

## この検証でやったこと・やらなかったこと

論文の主張は「推論トレース中の低エントロピーな構造トークン(`Wait,` `So,` `Let me double-check` など)をBPEでsupertoken化し、SFTでモデルに使わせることで、精度を落とさず思考の長さを平均8.1%短縮できる」というもの。

今回はフルのSFT再現(3モデルファミリー×5ベンチマーク)ではなく、**「supertoken化アルゴリズム自体が本当にトークン数を削減するか」という核となる主張の概念実証**に絞った。理由と制約は以下の通り。

- **公式データセット・トークナイザーはダウンロード不可**: 公式パイプラインは `open-thoughts/OpenThoughts3-1.2M` などのHugging Face上のデータセットと `Qwen/QwQ-32B` などのHugging Face上のトークナイザーを前提にしている。この実行環境ではネットワークポリシーにより `huggingface.co` へのアクセスがブロックされていることを確認した(`curl -sS https://huggingface.co` → `CONNECT tunnel failed, response 403`)。GitHub (`github.com`, `raw.githubusercontent.com`) は疎通した。
- そのため、**ベーストークナイザーは自前で用意**した(後述)。**推論トレースのコーパスも自作**した(公式データセットを使えないため)。
- 一方で、**n-gram集計・BPEマージ探索・supertoken適用のアルゴリズム本体は公式リポジトリのコードをそのまま呼び出している**(自前実装への置き換えはしていない)。具体的には:
  - `reastok.ngrams.count_ngrams` (n-gram集計)
  - `scripts/bpe_from_ngrams.run_bpe` (BPEマージ探索。フィルタなしのデフォルト設定)
  - `reastok.merge_apply.SuperPostTokenizer` (supertoken適用・トークン数計測)

このため、**論文の8.1%という数値の再現ではない**(コーパスもトークナイザーも別物なので直接比較はできない)。あくまで「同じアルゴリズムを動かしたら、方向性として同種の圧縮効果が観測できるか」の確認。

## セットアップ

```bash
python3 -m venv venv
./venv/bin/pip install tokenizers numpy safetensors
git clone https://github.com/Writer/shorthand-for-thought.git experiments/day-001/shorthand-for-thought
```

(実行時は `SHORTHAND_REPO` 環境変数でクローン先を指定できる。デフォルトは `./shorthand-for-thought`。)

依存バージョン: `tokenizers==0.23.2`, `numpy==2.4.6`, `safetensors==0.8.0` (Python 3.11.15)。

## 実行方法

```bash
cd experiments/day-001
SHORTHAND_REPO=./shorthand-for-thought ./venv/bin/python run_experiment.py
```

内容:

1. `corpus.py` の自作CoT風推論トレース(訓練16件・held-out 4件、四則演算・確率・論理パズルなどの解説文)を用意する。論文が扱う数学系推論トレースの構造(`Let me think step by step.` `Wait,` `So,` `Let me double-check` のような定型フレーズを多用する文体)を模した、筆者が書き下ろした文章であり、実際のLLM出力ではない。
2. `tokenizers` の `BpeTrainer` で、このコーパス上に語彙サイズ3000の小さなbyte-level BPEトークナイザーを**自前で学習**する(Qwen/QwQ-32Bトークナイザーの代替)。
3. 訓練データを1でエンコードし、`reastok.ngrams.count_ngrams` でn=2〜10のn-gramを集計する(サンプルあたりの出現上限10、公式の `config/datasets.yaml` のデフォルト値と同じ)。
4. `scripts/bpe_from_ngrams.run_bpe` で200回のBPEマージ(=supertoken)を探索する。
5. `reastok.merge_apply.SuperPostTokenizer` で、訓練データ・held-outデータそれぞれに対して、マージ数25/50/100/150/200の各チェックポイントでトークン数を計測し、ベーストークナイザーのみの場合と比較する。

## 結果概要

詳細な生ログ・数値は [results.md](./results.md) を参照。要点:

- held-out(訓練に使っていない4件の推論トレース)で、200マージ適用後に**トークン数が10.75%減少**した(744→664トークン)。
- 訓練データ(in-sample)では27.24%減少しており、in-sampleとheld-outで差があるのは想定通り(BPEマージはコーパスの頻出パターンに最適化されるため、未知データでは効果が薄まる)。
- 上位マージには `. So` `. Let` `-check` ` double-check` `. Let me double-check` など、論文が言う「構造的・低エントロピーな定型フレーズ」に対応するsupertokenが実際に出現した。

## 再現時の注意

- `experiments/day-001/shorthand-for-thought/` (公式リポジトリのクローン)はこのリポジトリには含めていない(ライセンス上コピーは可能だが、転載ではなく検証コードを主役にするため、READMEの手順で各自クローンしてもらう方針)。
- 本検証はCPUのみ・GPU不要・APIキー不要で完結する。
