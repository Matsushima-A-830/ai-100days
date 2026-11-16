# Day 049 — andrewyng/openworker をローカルLLM(llama.cpp)だけで動かす

出典: https://github.com/andrewyng/openworker (MIT License)

## やったこと

1. OpenWorker本体を`git clone`し、`bash packaging/setup_dev_env.sh`でPython製バックエンド
   (`coworker`パッケージ: エンジン・ツール・承認フロー・監査ログ)の開発環境を作った。
2. today.mdの計画ではOllamaを想定していたが、この実行環境では`ollama.com`への接続が
   ネットワークポリシーでブロックされていたため、OpenWorker自身が公式に対等な
   ローカルプロバイダとして扱っている**llama.cpp**(`llama-server`)に切り替えた。
   `ggml-org/llama.cpp`をソースからビルドし、Hugging Faceから取得した
   `Qwen2.5-1.5B-Instruct`(Apache-2.0)・`Qwen2.5-3B-Instruct`(非商用研究ライセンス)の
   GGUFモデルを`--jinja`付きで起動した。
3. OpenWorkerのCLI(`openworker run --isolated --model llamacpp:<alias> ...`)を使い、
   GUIなしでサーバーエンジン単体を直接動かした。
4. 「承認モードが`ask`で端末が無い場合、ツール呼び出しは実行前に拒否されて記録される」
   というOpenWorkerの"Governed by design"の主張を実際に再現した。
5. 承認を迂回するモード(`bypass-approvals`)で同じタスクを実行し、実際にファイルが
   書かれること・その操作も監査ログ(`audit.db`)に残ることを確認した。
6. 1.5B/3Bの2つのローカルモデルで、実際にタスクをやり切れるか(ファイルを読んで
   要約を書けるか)も観察した。

## 再現手順

```bash
git clone https://github.com/andrewyng/openworker /tmp/openworker-src
cd /tmp/openworker-src
bash packaging/setup_dev_env.sh

git clone --depth 1 https://github.com/ggml-org/llama.cpp /tmp/llama.cpp
cmake -B /tmp/llama.cpp/build -S /tmp/llama.cpp -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON
cmake --build /tmp/llama.cpp/build -j4 --target llama-server

mkdir -p /tmp/models
curl -L -o /tmp/models/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf

/tmp/llama.cpp/build/bin/llama-server -m /tmp/models/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  --alias qwen2.5-1.5b-instruct -c 8192 --jinja --host 127.0.0.1 --port 8080 &

mkdir -p /tmp/ow-workspace-ask
cp notes1.md notes2.md /tmp/ow-workspace-ask/

cd /tmp/openworker-src
.venv/bin/openworker run --isolated \
  --workspace /tmp/ow-workspace-ask \
  --model "llamacpp:qwen2.5-1.5b-instruct" \
  --approval-mode ask \
  --out /tmp/ow-out-ask \
  --timeout-seconds 150 \
  --prompt "Write a file named brief.md containing a 3-line summary of notes1.md and notes2.md. Do it now, call the write_file tool directly without asking me first."
```

完全なコマンド列(3Bモデルでの再試行を含む)は`setup.sh`を参照。
検証用のメモ2本は`notes1.md`・`notes2.md`。

詳細な実行ログ・つまずいた点・最終結果は`results.md`を参照。生の出力・JSONログは
`logs/`以下にまとめた。
