# Day 047 — lidge-jun/opencodex

出典: https://github.com/lidge-jun/opencodex (npm: `@bitkyc08/opencodex`, MIT, 検証時バージョン `2.100.2`)

OpenAI Codex・Claude Code・Claude Desktop等のコーディングエージェントと、Claude/Gemini/Grok/
DeepSeek/ローカルOllama等の各モデルプロバイダーの間に立つローカルゲートウェイ。
Responses API・Chat Completions API・Anthropic Messages APIの各形式を相互変換する。

詳細な検証過程・出力ログは [`results.md`](./results.md) を参照。

## 再現手順

```bash
# 1. インストール
npm install -g --allow-scripts=bun @bitkyc08/opencodex
ocx --version   # opencodex 2.100.2

# 2. OpenAI Chat Completions互換のバックエンドを用意する
#    実機のOllamaなら `ollama serve` だけで localhost:11434 に立つ。
#    本検証ではOllamaのインストール元ホスト(ollama.com)がRoutine実行環境の
#    ネットワークポリシーでブロックされていたため、同じポートで動く最小限の
#    モックサーバー(本ディレクトリの mock_ollama_server.js)を使った。
node mock_ollama_server.js &

# 3. プロバイダとして登録してプロキシを起動
ocx provider add my-ollama --adapter openai-chat --base-url http://localhost:11434/v1 \
  --default-model mock-model --allow-private-network --auth-mode local --set-default --json
ocx start

# 4. Anthropic Messages API形式でリクエストを送る
curl -s -X POST http://localhost:10100/v1/messages \
  -H "Content-Type: application/json" -H "x-api-key: dummy" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"my-ollama/mock-model","max_tokens":64,"messages":[{"role":"user","content":"hello"}]}'
```

実機のOllamaで追試する場合は、手順2を `ollama pull <モデル名>` と `ollama serve` に置き換え、
手順4の `model` を実際に`pull`したモデル名に変える。
Ollama自体が`/v1/chat/completions`でOpenAI Chat Completions互換かつSSEストリーミング対応の
エンドポイントを提供しているため、本検証で使ったモックサーバーと同じ条件を満たす。

## 含まれるファイル

- `mock_ollama_server.js`: Ollama代替の最小HTTPサーバー(OpenAI Chat Completions互換、
  非ストリーミング/ストリーミング〈SSE〉の両方に対応)。
- `results.md`: 実行ログと検証結果の詳細。
- `install_log/npm_install.log`: `npm install -g`の実行ログ。
- `provider_add.log`: `ocx provider add`の実行ログ(JSON)。
- `mock_ollama.log`: モックサーバーが受け取った実際のリクエスト(ヘッダ・ボディ)のログ。

## スコープについて(today.md記載の方針)

実際のClaude Code/Codexの製品アカウント(サブスクリプションログイン)は使わず、
Anthropic Messages API形式のリクエストをcurl等で直接プロキシに送って変換・転送を確認する
検証に絞った。opencodex公式READMEの「Disclaimer」節に、Anthropic等が非公式プロキシ経由の
アカウントを停止・制限する可能性があると明記されているため。
