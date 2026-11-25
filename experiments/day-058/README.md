# Day 058: OpenSRE (Tracer-Cloud) — 有料APIキー無しでCI障害を調査させる

出典: https://github.com/Tracer-Cloud/opensre (Apache-2.0。PyPI配布版 `opensre` 2026.4.5)

CIが落ちたときにログを読んで根本原因を調べる、自己ホスト型のAIエージェント。
本チャレンジの方針(「有料APIキー必須の候補は選ばない」)に沿い、ホスト型モデルへのサインインは使わず、
ローカルのOllamaをLLMとして使った。詳細な結果は `results.md`、ローカル検証のファイル一式は `local/`。

## 再現手順(CLIの挙動)

```bash
python3 -m venv .venv && .venv/bin/pip install opensre
export DO_NOT_TRACK=1            # 利用状況の送信(PostHog)を止める
.venv/bin/opensre --version
.venv/bin/opensre doctor
.venv/bin/opensre health

# LLMプロバイダ未設定のままRCA調査 → ValidationErrorでクラッシュ
.venv/bin/opensre investigate --print-template generic > alert.json
.venv/bin/opensre investigate -i alert.json

# Ollamaをプロバイダに指定(Ollama未起動だとplan_actionsで失敗)
LLM_PROVIDER=ollama .venv/bin/opensre investigate -i alert.json
```

## 再現手順(壊したCIを調査させる、`local/`)

```bash
# 1. OpenSREのコンテナ(local/Dockerfile)
docker build -t day058-opensre:2026.4.5 local/

# 2. Ollama(CPU推論で実行した。GPUがあれば CUDA_VISIBLE_DEVICES は不要)
ollama pull qwen2.5:7b-instruct
CUDA_VISIBLE_DEVICES=-1 OLLAMA_HOST=127.0.0.1:11599 ollama serve &

# 3. ダミーリポジトリのCI(main は成功、feature/fast-total は test_rounding が失敗)
#    local/invoice-calc は main の中身、local/feature-fast-total.diff が壊す変更
#    ログは local/ci-main.log / local/ci-feature-fast-total.log

# 4. CIログ入りのアラートを調査させる(作業ディレクトリ $HOME/.cache/day058-work に alert_*.json を置く)
local/run_inv.sh qwen2.5:7b-instruct alert_v1_log.json q7-v1-r1
local/run_inv.sh qwen2.5:7b-instruct alert_v2_log_diff.json q7-v2-r1
```

## ファイル

- `results.md` — 全ての実行結果(1〜5章: CLIの挙動、6章: ローカル検証)
- `local/Dockerfile` — OpenSRE 2026.4.5の実行コンテナ(`DO_NOT_TRACK=1`)
- `local/invoice-calc/` — 壊す対象のダミーリポジトリ(`main`の状態、`.github/workflows/ci.yml`付き)
- `local/feature-fast-total.diff` — `round(..., 2)` を `int(... * 100) / 100` に変えた壊す変更
- `local/ci.sh`, `local/ci-*.log` — ワークフローと同じ手順のCI実行スクリプトとログ
- `local/alert_v1_log.json`, `local/alert_v2_log_diff.json` — OpenSREに渡したアラート(CIログ / CIログ+diff)
- `local/run_inv.sh` — 調査1回分の実行スクリプト
- `local/out/` — 6回の調査のログ(`*.log`)・レポート(`*.json`)・一覧(`runs.txt`)
