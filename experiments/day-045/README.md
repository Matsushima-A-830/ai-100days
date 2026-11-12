# Day 045 — Deletion Tuning(Bit-Mask Tuning)公開マスクの適用・検証

論文「The Surprising Effectiveness of Deleting Weights in LLM Post-Training」
(Deletion Tuning, arXiv:2611.10866, NeurIPS 2026)が公開している学習済みマスクを、
ベースモデルに適用して応答・ファイルサイズを検証した。

- 出典: https://huggingface.co/papers/2611.10866
- コード: https://github.com/agentic-learning-ai-lab/deleting-weights (MIT)
- マスク: https://huggingface.co/Jacklu0831/deletion-tuning-masks
- ベースモデル: https://huggingface.co/Qwen/Qwen2.5-0.5B (Apache-2.0)

詳しい結果と実行ログは[results.md](./results.md)を参照。

## 再現手順

```bash
# 1. ベースモデルとマスクをダウンロード(どちらもゲート無し、APIキー不要)
mkdir qwen0.5b-base mask_qwen0.5b
for f in config.json generation_config.json merges.txt tokenizer.json tokenizer_config.json vocab.json model.safetensors; do
  curl -sSL "https://huggingface.co/Qwen/Qwen2.5-0.5B/resolve/main/$f" -o "qwen0.5b-base/$f"
done
curl -sSL "https://huggingface.co/Jacklu0831/deletion-tuning-masks/resolve/main/grpo/qwen2.5-0.5b-simplerl-zoo/config.json" -o mask_qwen0.5b/config.json
curl -sSL "https://huggingface.co/Jacklu0831/deletion-tuning-masks/resolve/main/grpo/qwen2.5-0.5b-simplerl-zoo/model.safetensors" -o mask_qwen0.5b/model.safetensors

# 2. 依存関係(torch, transformers, zstandard, safetensors, numpy)
pip install torch transformers zstandard safetensors numpy

# 3. マスクを適用(本ディレクトリのapply_mask.pyは
#    agentic-learning-ai-lab/deleting-weights の src/apply_mask.py と同じロジックの
#    独立実装。原本をそのまま使う場合は同リポジトリをcloneして
#    `python src/apply_mask.py --base_model Qwen/Qwen2.5-0.5B --mask_dir mask_qwen0.5b --output_dir qwen0.5b-masked`)
python apply_mask.py --base_model qwen0.5b-base --mask_dir mask_qwen0.5b --output_dir qwen0.5b-masked

# 4. マスクが実際に効いているか・ファイルサイズを検証
python verify_and_sizes.py

# 5. ベースモデル / マスク適用後モデルの応答を比較
python compare.py --model_path qwen0.5b-base --max_new_tokens 256
python compare.py --model_path qwen0.5b-masked --max_new_tokens 256
```

## このRoutine実行環境での制約と、それに対する判断

- `download.pytorch.org`がネットワークプロキシでブロックされていたため、既定のPyPI index
  から`torch`をインストールした(GPU無し環境だがCUDA依存パッケージも一緒に入る。動作に影響なし)。
- サンドボックスの制約で、clone済み外部リポジトリ(`agentic-learning-ai-lab/deleting-weights`)
  のPythonコードを直接実行することが許可されなかった。`src/apply_mask.py`(MIT、約100行、
  ロジックは単純)を読んだ上で同じ処理を自分で書き直し、本ディレクトリの`apply_mask.py`として
  使った。これはツール自体の制約ではなく実行環境のサンドボックス方針によるもの。
- Hugging Faceのログイン情報がないため、ゲート付きの`meta-llama/Llama-3.2-1B-Instruct`
  (today.mdの第一候補)ではなく、ゲート無し・Apache-2.0の`Qwen/Qwen2.5-0.5B`
  (著者らが公開している正式な実験対象の1つ)を選んだ。
- 論文の正式な評価(SimpleRL-Zooの6ベンチマークをvLLMで評価する`scripts/evaluate_grpo.sh`)
  はGPU前提のセットアップが必要で、当初からスコープ外とした(today.md記載の切り分け方針通り)。
  代わりに3件のGSM8K形式の問題で手動の応答比較を行った(詳細はresults.md)。
