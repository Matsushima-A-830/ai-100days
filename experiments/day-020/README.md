# Day 020: SAE Additivity Residuals (SAR) を GPT-2 Small で再現する

対象: 論文 "Behavioral Compositionality of Sparse Autoencoder Representations"
(Ziye Mei, Frederic Sala, University of Wisconsin–Madison)
https://huggingface.co/papers/2610.21261

コード: [OpenSAE/SAE-Behavioral-Compositionality](https://github.com/OpenSAE/SAE-Behavioral-Compositionality) (Apache-2.0)

詳しい結果・考察は [`results.md`](./results.md) を参照。ここでは再現手順のみまとめる。

## 事前準備

- Python 3.11以上(本検証はPython 3.11.17で実施)
- 追加の有料APIキーは不要。GPUも不要(CPUのみで約4分で完走)。
- `gpt2`モデル・`gpt2-small-res-jb` SAEはいずれも公開されており、
  HuggingFace Hubから自動ダウンロードされる(認証不要)。

## 再現手順

```bash
cd experiments/day-020
python3 -m venv venv
source venv/bin/activate

# 公式のrequirements_demo.txt はPython 3.12前提でnumpy==2.5.0を固定しているが、
# Python 3.11では見つからないため、ここではバージョンを緩めてインストールする
# (詳細はresults.md 1節)。
pip install numpy matplotlib torch transformer-lens==3.5.0 sae-lens==6.44.4

# layer 4, 10 の両方でSARを計算し、4パネルの図を保存する
python3 demo/demo.py --layers 4 10
```

## このディレクトリの内容

- `sar.py` — SAR推定器本体(NumPyのみに依存)。上流リポジトリから無改変で取得。
- `demo/demo.py` — GPT-2 Small + `gpt2-small-res-jb` を使った再現デモ本体。
  上流リポジトリから無改変で取得。
- `LICENSE-upstream` — 上記2ファイルの出典元リポジトリのライセンス全文(Apache-2.0)。
- `demo_layers4_10.png` — 実際に実行して得られた図(layer 4, 10の比較)。
- `results.md` — 検証の過程・実際の実行ログ・結果の読み方・結論。
