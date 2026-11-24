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

### ローカル検証(GPU/CPU・BF16/FP32、NQ 300問)

```bash
# 同じスクリプトをデバイスとdtypeだけ変えて実行(結果は実行したディレクトリに書き出される)
.venv/bin/python run_device.py 02_qa_compare.py cuda bf16   # cuda|cpu, bf16|fp32
python3 grade_devices.py PR=. cpu-bf16=device_runs/cpu-bf16 cuda-bf16=device_runs/cuda-bf16 cpu-fp32=device_runs/cpu-fp32 cuda-fp32=device_runs/cuda-fp32

# Natural Questions(DPR形式のdev split)300問に拡大
# データ(約150MB)を取得
mkdir -p data && curl -L -o data/nq-dev.jsonl.gz https://huggingface.co/datasets/Tevatron/wikipedia-nq/resolve/main/nq-dev.jsonl.gz
.venv/bin/python 04_nq_scale.py 300 cpu bf16 nq_scale_results.jsonl   # CPUで約53分
python3 summarize_nq.py nq_scale_results.jsonl
```

## ファイル

- `01_reproduce_cards.py`: QueryLM / Standardのモデルカード記載コードをそのまま実行(動作確認)。
- `02_qa_compare.py`: 8問の知識QAで3条件(QueryLM検索なし/あり、Standard)を比較。`qa_results.json` に生成結果を保存。
- `03_sft_variant.py`: チャット微調整版 `querylm-wiki-360m-sft-search` で同じ8問を試す。`sft_results.json` に保存。
- `run_device.py`: 01〜03をそのまま、デバイス(cpu/cuda)とdtype(bf16/fp32)だけ差し替えて実行するラッパー。
- `grade_devices.py`: 8問の結果を共通の基準で採点して比較表を出す。
- `device_runs/`: 8問をCPU/GPU×BF16/FP32で再実行したログと結果。
- `04_nq_scale.py` / `summarize_nq.py`: Natural Questions 300問への拡大と集計。`nq_scale_results.jsonl` に全生成結果、`logs_nq_scale.txt` / `logs_nq_summary.txt` にログ。
- `data/`: NQのデータ(リポジトリにはコミットしない)。
- `logs_*.txt`: 各スクリプトの標準出力ログ。
- `results.md`: 結果と考察。
- `models/`: ダウンロードしたモデル重み(リポジトリにはコミットしない。`.gitignore` 参照)。

## 使用モデル(いずれもApache-2.0、361.8Mパラメータ・BF16)

- `Kausp11/querylm-wiki-360m` — search-native事前学習ベースモデル
- `Kausp11/standard-wiki-360m` — 同条件・検索ブロックなしのベースライン
- `Kausp11/querylm-wiki-360m-sft-search` — QueryLMのチャット微調整版
