# Day 059: p-e-w/heretic (training-free abliteration) をCPUのみで動かす

出典: https://github.com/p-e-w/heretic (AGPL-3.0-or-later)

Optunaによるパラメータ自動探索で、追加学習なしにLLMの拒否挙動(安全アラインメント)を抑制する
`heretic-llm`を、GPUの無い環境でも動くようスケールダウンして実際に実行した。
倫理面の方針・詳細な結果は[`results.md`](./results.md)を参照。

## 再現手順

```bash
cd experiments/day-059
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install heretic-llm transformers accelerate

# 1. 処理前のベースライン応答(無害な質問のみ)を記録
.venv/bin/python baseline_test.py Qwen/Qwen3-0.6B baseline_responses_before.json

# 2. heretic本体のOptuna最適化(本ディレクトリのconfig.tomlがCPU用に縮小した設定)
HERETIC_CONFIG_FILE=./config.toml .venv/bin/heretic \
  --model Qwen/Qwen3-0.6B \
  --checkpoint-action restart \
  --trial-index 0 \
  --model-action save \
  --export-strategy merge \
  --save-directory /tmp/heretic-day059-model \
  > heretic_run.log 2>&1

# 3. 処理後モデルで同じ無害な質問を再度確認
.venv/bin/python baseline_test.py /tmp/heretic-day059-model baseline_responses_after.json

# 4. 検証終了後、処理後モデルの重みは削除する(外部に公開・配布しない方針)
rm -rf /tmp/heretic-day059-model
```

`config.toml`の内容(upstream既定値との差分)は`results.md`の表を参照。
`checkpoints/`(Optunaのstudyチェックポイント)は`.gitignore`で除外している。

## 所要時間

- `pip install heretic-llm`: 数分(初回のみ、torch等の依存を含む)
- Optuna最適化12 trial: **CPUで12分17秒**(heretic自身の計測、`Qwen/Qwen3-0.6B`)
- モデル読み込み・マージ保存まで含めたスクリプト全体: 概ね14〜15分

## ファイル

- `config.toml`: heretic用の設定(CPU用に縮小)
- `baseline_test.py`: 無害な質問での処理前/処理後比較スクリプト
- `baseline_responses_before.json` / `baseline_responses_after.json`: その生成結果
- `heretic_run.log`: heretic実行時の標準出力(個々の有害プロンプト・応答は含まない。集計スコアのみ)
- `results.md`: 詳細な結果・倫理面の方針・制約
