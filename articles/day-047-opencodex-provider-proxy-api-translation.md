---
title: "コーディングエージェント用プロバイダープロキシopencodexで、Anthropic/OpenAI 3形式のAPI変換を試した"
emoji: "🔌"
type: "tech"
topics: ["ai", "llm", "ollama", "anthropic", "openai"]
published: false
---

## これは何を試した記事か

[lidge-jun/opencodex](https://github.com/lidge-jun/opencodex)(npm: `@bitkyc08/opencodex`、MIT)は、OpenAI Codex・Claude Code・Claude Desktop・Grok Build等のコーディングエージェントと、Claude/Gemini/Grok/DeepSeek/ローカルOllama等の各モデルプロバイダーの間に立つローカルゲートウェイである。
GitHub TrendingのTypeScript部門で1日+55starを集めていた。

売りは、Responses API・OpenAI Chat Completions API・Anthropic Messages APIという3つのAPI形式を相互変換し、エージェント側のベースURLを`http://localhost:10100/v1`に向けるだけで任意のプロバイダに接続できる点である。
`provider/model`形式でのモデル指定や、複数プロバイダへのフェイルオーバー/重み付きラウンドロビン(「コンボ」)にも対応するという。

本記事では「本来は有料APIの契約が前提になりがちなコーディングエージェントを、ローカルのモデルにルーティングできる」という核心機能のうち、API形式変換・転送そのものを実際に動かして確認した。

- 出典: https://github.com/lidge-jun/opencodex (MIT、検証時バージョン `2.100.2`)
- 日本語記事件数(2026-11-13時点、Zenn/Qiita/note検索): 0件

## 検証のスコープを絞った理由

opencodex公式READMEの「Disclaimer」節には、次のように明記されている。

> Some providers — notably Anthropic (Claude) — may suspend or restrict accounts that route API traffic through third-party proxies. **Use at your own risk (UAYOR).**

このため本検証では、実際のClaude Code/Codexの製品アカウント(サブスクリプションログイン)は使わず、Anthropic Messages API形式のリクエストをcurlで直接プロキシに送って、変換・転送が正しく行われるかの確認に絞った。

バックエンドとしては、本来はローカルOllamaを使う想定だったが、筆者の検証環境(クラウドのRoutine実行環境)のネットワークポリシーが`ollama.com`への到達を許可していなかった。
そこで、opencodexが要求する条件(OpenAI Chat Completions互換の`/v1/chat/completions`エンドポイントを持つこと)だけを満たす最小限のモックサーバーを自分で書いて、代わりに使った。
Ollama自体もこの`/v1/chat/completions`をSSEストリーミング対応で提供しているため、この検証はopencodexが実際にやっていること(API形式変換の中継)を直接確認できている。

## インストール

```bash
$ npm install -g --allow-scripts=bun @bitkyc08/opencodex

added 102 packages in 8s

$ ocx --version
opencodex 2.100.2
```

npmのグローバルインストールだけで完了した。
インストール先の`LICENSE`ファイルを直接確認し、標準的なMIT Licenseの文言であることを確認した。

## モックバックエンドの用意とプロバイダ登録

Ollamaの既定ポート(`11434`)で、`/v1/chat/completions`だけを実装した最小限のNode.jsサーバーを立てた。

```bash
$ node mock_ollama_server.js &
[mock-ollama] listening on http://localhost:11434
```

公式ヘルプに載っている例そのままの形で、カスタムプロバイダとして登録する。

```bash
$ ocx provider add my-ollama --adapter openai-chat --base-url http://localhost:11434/v1 \
    --default-model mock-model --allow-private-network --auth-mode local --set-default --json
{
  "action": "added",
  "provider": "my-ollama",
  "adapter": "openai-chat",
  "baseUrl": "http://localhost:11434/v1",
  "isDefault": true
}

$ ocx start
🚀 opencodex proxy running on http://localhost:10100
   POST /v1/responses → provider translation
   POST /v1/chat/completions → OpenAI-compatible clients
```

## 1回目は502で失敗した

Anthropic Messages API形式でリクエストを送ってみると、最初は502になった。

```bash
$ curl -s -X POST http://localhost:10100/v1/messages \
    -H "Content-Type: application/json" -H "x-api-key: dummy" \
    -H "anthropic-version: 2023-06-01" \
    -d '{"model":"my-ollama/mock-model","max_tokens":64,"messages":[{"role":"user","content":"..."}]}'

{"type":"error","error":{"type":"overloaded_error","message":"The provider failed to complete the request."}}
```

モックサーバーのログを見ると、原因が分かった。
opencodexはバックエンドへの転送時に`"stream":true`を付けていたが、筆者の最初のモック実装は通常のJSON(非ストリーミング)しか返せなかったため、応答を解釈できず失敗していた。

```
[mock-ollama] body: {"model":"mock-model","messages":[...],"stream":true,"stream_options":{"include_usage":true}}
```

これはopencodexの実装上の挙動(OpenAI互換バックエンドには既定でストリーミングを要求する)であり、Ollama自体は`/v1/chat/completions`でSSEストリーミングに対応しているため、実機のOllamaなら発生しない問題と考えられる。
モックサーバーにSSE(`data: {...}\n\n`の連続+`data: [DONE]`)での応答を追加して再検証した。

## 3つの受け口形式すべてで変換に成功

同じバックエンドに対し、opencodexが対応する3つの受け口形式すべてでリクエストを送った。

```bash
# Anthropic Messages API形式
$ curl -s -X POST http://localhost:10100/v1/messages \
    -H "x-api-key: dummy" -H "anthropic-version: 2023-06-01" \
    -d '{"model":"my-ollama/mock-model","max_tokens":64,"messages":[{"role":"user","content":"こんにちは"}]}'

{"id":"msg_27a3533f...","type":"message","role":"assistant",
 "content":[{"type":"text","text":"Hello from the mock Ollama backend. opencodex proxied this correctly."}],
 "model":"my-ollama/mock-model","stop_reason":"end_turn"}
```

```bash
# OpenAI Chat Completions形式
$ curl -s -X POST http://localhost:10100/v1/chat/completions \
    -d '{"model":"my-ollama/mock-model","messages":[{"role":"user","content":"..."}]}'

{"id":"chatcmpl-mock-001","object":"chat.completion",
 "choices":[{"message":{"role":"assistant","content":"Hello from the mock Ollama backend. opencodex proxied this correctly."},"finish_reason":"stop"}]}
```

```bash
# OpenAI Responses API形式
$ curl -s -X POST http://localhost:10100/v1/responses \
    -d '{"model":"my-ollama/mock-model","input":"..."}'

{"id":"resp_1c0d479a...","object":"response","status":"completed",
 "output":[{"type":"message","role":"assistant","content":[{"type":"output_text","text":"Hello from the mock Ollama backend. opencodex proxied this correctly."}]}]}
```

| 送信した形式(inbound) | エンドポイント | 結果 |
|---|---|---|
| Anthropic Messages API | `POST /v1/messages` | ✅ 200(Anthropic形式の応答に変換済み) |
| OpenAI Chat Completions | `POST /v1/chat/completions` | ✅ 200(OpenAI Chat Completions形式の応答) |
| OpenAI Responses API | `POST /v1/responses` | ✅ 200(Responses形式の応答に変換済み) |

同じ1つのOpenAI Chat Completions互換バックエンドに対し、3つの異なるAPI形式のリクエストすべてが正しく変換・転送され、それぞれの形式に応じた応答に変換し直されて返ってきた。
`provider/model`形式でモデルを指定し、ベースURLを`http://localhost:10100/v1`に向けるだけで任意のプロバイダに接続できるという、opencodexの核心的な価値提案にあたる部分を確認できた。

## ライセンスと利用上の注意

- `LICENSE`: MIT License。
- README「Disclaimer」節: opencodexは独立したコミュニティメンテナンスのプロジェクトで、OpenAI・Anthropic等の提供元とは無関係。Anthropic等が非公式プロキシ経由のアカウントを停止・制限する可能性があると明記されている。実際にClaude Code/Codexの製品ログインを通す場合は、各プロバイダの利用規約を確認した上で自己責任(UAYOR)で行う必要がある。

## まとめ

- `npm install -g`だけでインストールが完了し、公式ヘルプの手順でカスタムプロバイダを登録できた。
- 最初のモックは非ストリーミング応答しか返せず502で失敗したが、これはopencodexがバックエンドへの転送時に`stream:true`を既定で要求するためだった。SSE対応に直すと成功した。
- Anthropic Messages API・OpenAI Chat Completions・OpenAI Responses APIの3つの受け口すべてで、同じバックエンドへの変換・転送と、元の形式への応答変換が正しく機能した。
- 本検証では実際のClaude Code/Codexの製品ログインは使わず、API形式の変換・転送という本質的な機能に絞った。アカウントリスクに関する公式の免責事項がある以上、実際の製品アカウントで試す場合は利用規約を確認した上で自己責任で行う必要がある。
