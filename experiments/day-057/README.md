# Day 057: QueryLM (search-native pretraining) vs Standard baseline — 360M

出典: 論文 [Search From the Start: Search-Native Pretraining for Language Models](https://arxiv.org/abs/2611.26809)(arXiv:2611.26809)。
モデル群(Apache-2.0): https://huggingface.co/collections/Kausp11/search-native-pretraining
プロジェクトページ: https://kaustubhp11.github.io/querylm

事前学習の段階から検索クエリを発行させる「search-native」な学習をした360MモデルQueryLMと、同architecture・同computeのStandardベースラインを、
Hugging Faceから取得して実際にCPU推論で比較した。詳細な結果は `results.md` を参照。

## 再現手順

```bash
python3 -m venv .venv && .venv/bin/pip install --upgrade pip
.venv/bin/pip install torch --extra-index-url https://pypi.org/simple
.venv/bin/pip install transformers huggingface_hub accelerate safetensors

python3 - <<'PY'
from huggingface_hub import snapshot_download
for repo in ["Kausp11/querylm-wiki-360m", "Kausp11/standard-wiki-360m", "Kausp11/querylm-wiki-360m-sft-search"]:
    snapshot_download(repo_id=repo, local_dir="models/" + repo.split("/")[1])
PY

.venv/bin/python 01_reproduce_cards.py   # モデルカードの使用例をそのまま再現
.venv/bin/python 02_qa_compare.py        # 8問の知識QAで QueryLM(検索なし/あり) vs Standard を比較
.venv/bin/python 03_sft_variant.py       # チャット微調整版(sft-search)で同じ8問
```

## ファイル

- `01_reproduce_cards.py`: QueryLM / Standardのモデルカード記載コードをそのまま実行(動作確認)。
- `02_qa_compare.py`: 8問の知識QAで3条件(QueryLM検索なし/あり、Standard)を比較。`qa_results.json` に生成結果を保存。
- `03_sft_variant.py`: チャット微調整版 `querylm-wiki-360m-sft-search` で同じ8問を試す。`sft_results.json` に保存。
- `logs_*.txt`: 各スクリプトの標準出力ログ。
- `results.md`: 結果と考察。
- `models/`: ダウンロードしたモデル重み(リポジトリにはコミットしない。`.gitignore` 参照)。

## 使用モデル(いずれもApache-2.0、361.8Mパラメータ・BF16)

- `Kausp11/querylm-wiki-360m` — search-native事前学習ベースモデル
- `Kausp11/standard-wiki-360m` — 同条件・検索ブロックなしのベースライン
- `Kausp11/querylm-wiki-360m-sft-search` — QueryLMのチャット微調整版
