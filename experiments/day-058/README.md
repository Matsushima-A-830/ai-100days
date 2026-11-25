# Day 058: OpenSRE (Tracer-Cloud) — 有料APIキー無しでどこまで動くCI/CD信頼性エージェントか

出典: https://github.com/Tracer-Cloud/opensre (Apache-2.0。PyPI配布版 `opensre` 2026.4.5)

CIが落ちたときにログを読んで根本原因を調べ、修正案をPRに出すという自己ホスト型AIエージェント。
本チャレンジの方針(「有料APIキー必須の候補は選ばない」)に沿い、**ホスト型モデルへのサインインは使わず、
`opensre onboard local_llm`(OllamaによるゼロコンフィグなローカルLLM導線)を使う前提で検証した**。
詳細な結果は `results.md` を参照。

## 再現手順

```bash
python3 -m venv .venv && .venv/bin/pip install opensre
.venv/bin/opensre --version
.venv/bin/opensre doctor
.venv/bin/opensre health

# ゼロコンフィグのローカルLLM導線(Ollamaが無ければ公式インストーラを実行する)
echo y | .venv/bin/opensre onboard local_llm

# LLMプロバイダ未設定のままRCA調査を試みる
.venv/bin/opensre investigate --print-template generic > alert.json
.venv/bin/opensre investigate -i alert.json

# Ollamaをプロバイダに明示指定した場合
LLM_PROVIDER=ollama .venv/bin/opensre investigate -i alert.json
```

## このRoutine実行環境で到達できなかった部分(ローカル検証が必要)

`opensre onboard local_llm` は、Ollama未導入時に公式インストールコマンド
(`curl -fsSL https://ollama.com/install.sh | sh`)を実行しようとするが、
このRoutineのクラウド実行環境ではネットワークポリシーにより `ollama.com` への
アウトバウンド接続がブロックされている(Routine環境固有の制約。通常の開発者PCには無い制限)。
そのため、実際にOllama上でモデルを動かし、CI障害の調査→修正PR提案までを行う本来の検証
(today.md記載の計画: 本リポジトリにダミーの壊れたCI/PRを用意し、`opensre`に調査させる)は
今回は実行できなかった。**ローカル検証が必要。**

ローカル検証の手順(Ollamaが動く開発者PCで実行):

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b   # または他の軽量モデル
python3 -m venv .venv && .venv/bin/pip install opensre
LLM_PROVIDER=ollama OLLAMA_MODEL=qwen2.5:7b .venv/bin/opensre onboard local_llm
# その後、意図的にlintエラー等を仕込んだブランチ+PRを用意し、
# `opensre investigate` または `opensre ask` でCI失敗を調査させる
```

なお、本リポジトリ (ai-100days) 自体には GitHub Actions のCIワークフローが存在しないため
(`.github/workflows/` なし)、today.md が想定していた「本リポジトリ自身のCIを壊す」自己言及的な
デモは、ワークフローを新設しない限りそもそも成立しない。ローカル検証では、壊すCIは
別の小さなダミーリポジトリ(またはOpenSREのソースチェックアウト自身が持つ `make lint` 等)を
使うことを推奨する。

## 実際にRoutine環境で検証できたこと

Ollama自体は動かせなかったが、`opensre` というツール自身のCLI挙動・設定モデル・
エラーハンドリングは実際に手を動かして検証できた。詳細は `results.md`。
