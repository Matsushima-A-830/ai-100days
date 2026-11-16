#!/usr/bin/env bash
# Day 049 — andrewyng/openworker をローカルLLM(llama.cpp)だけで動かす再現手順
set -euo pipefail

# 1. OpenWorker本体をclone
git clone https://github.com/andrewyng/openworker /tmp/openworker-src
cd /tmp/openworker-src
bash packaging/setup_dev_env.sh   # .venv にPython依存(aisuite, coworker等)を導入

# 2. llama.cpp をソースからビルド(Ollamaはこの実行環境ではネットワーク制限でブロックされるため)
git clone --depth 1 https://github.com/ggml-org/llama.cpp /tmp/llama.cpp
cd /tmp/llama.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON
cmake --build build -j4 --target llama-server

# 3. ローカルモデル(Qwen2.5, MITではなくApache-2.0相当のQwenライセンス、商用利用可)をHugging Faceから取得
mkdir -p /tmp/models
curl -L -o /tmp/models/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf
curl -L -o /tmp/models/qwen2.5-3b-instruct-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf

# 4. llama-server を起動(OpenWorker自身がMacで `llama-server` を起動する時と同じフラグ: --jinja)
/tmp/llama.cpp/build/bin/llama-server -m /tmp/models/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  --alias qwen2.5-1.5b-instruct -c 8192 --jinja --host 127.0.0.1 --port 8080 &

# 5. 検証用ワークスペース(会議メモ2本)を用意
mkdir -p /tmp/ow-workspace-ask
cp notes1.md notes2.md /tmp/ow-workspace-ask/   # experiments/day-049/notes1.md, notes2.md を参照

# 6a. 承認フローの確認: --approval-mode ask(端末なし)→ 拒否されて記録されることを確認
cd /tmp/openworker-src
.venv/bin/openworker run --isolated \
  --workspace /tmp/ow-workspace-ask \
  --model "llamacpp:qwen2.5-1.5b-instruct" \
  --approval-mode ask \
  --out /tmp/ow-out-ask \
  --timeout-seconds 150 \
  --prompt "Write a file named brief.md containing a 3-line summary of notes1.md and notes2.md. Do it now, call the write_file tool directly without asking me first."

# 6b. 承認を明示的にbypassした場合: 実際にファイルが書かれることを確認
.venv/bin/openworker run --isolated \
  --workspace /tmp/ow-workspace-ask \
  --model "llamacpp:qwen2.5-1.5b-instruct" \
  --approval-mode bypass-approvals \
  --out /tmp/ow-out-bypass \
  --timeout-seconds 150 \
  --prompt "Write a file named brief.md containing a 3-line summary of notes1.md and notes2.md. Do it now, call the write_file tool directly without asking me first."

# 6c. 少し大きいローカルモデル(3B)での同じタスク(README本来の例題: フォルダのメモからbrief.mdを作る)
# ポート8080を3Bモデルのllama-serverに差し替えて実行
.venv/bin/openworker run --isolated \
  --workspace /tmp/ow-workspace-ask \
  --model "llamacpp:qwen2.5-3b-instruct" \
  --approval-mode bypass-approvals \
  --out /tmp/ow-out-3b \
  --timeout-seconds 200 \
  --prompt "Read the meeting notes in this folder. Create a one-page brief with the key decisions, open questions and next steps. Save it as brief.md."
