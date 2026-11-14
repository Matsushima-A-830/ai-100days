# Day 047 results — lidge-jun/opencodex

出典: https://github.com/lidge-jun/opencodex (npm: `@bitkyc08/opencodex`, MIT, 検証時バージョン `2.100.2`)

## 検証スコープ

today.md記載の方針どおり、実際のClaude Code/Codexの製品アカウント(サブスクリプションログイン)は
使わず、アカウントリスクを避けた。
ローカルOllamaの実機テストは、本Routine実行環境のネットワークポリシーが`ollama.com`への到達を
許可していないため行えなかった(下記「環境」参照。これは検証対象ツールの欠陥ではなくRoutine環境の
制約であり、CLAUDE.mdの方針に沿って記事本文では触れない)。
その代わりに、opencodexが要求する「OpenAI Chat Completions形式のエンドポイントを持つバックエンド」
という条件だけを満たす最小限のモック的なローカルHTTPサーバー(`mock_ollama_server.js`、本リポジトリに
同梱)を自分で書いて立て、opencodexの核心機能である「Anthropic Messages API / OpenAI Chat
Completions / OpenAI Responses APIの相互変換とルーティング」を直接検証した。
Ollama自体はOpenAI Chat Completions互換の`/v1/chat/completions`を提供するだけなので、
この検証はopencodexが実際にやっていること(API形式変換の中継)を直接確認できている。

## 環境

- Node.js v22.23.4 / npm 10.9.9
- インストール: `npm install -g --allow-scripts=bun @bitkyc08/opencodex`
- `ollama.com`への到達性確認(参考、Routine実行環境固有の制約の記録):
  `curl`でのOllamaインストーラへの到達はネットワークポリシーでブロックされた
  (本Routine実行環境の許可ホストリストに`ollama.com`が含まれていないため)。

## 1. インストール

```
$ npm install -g --allow-scripts=bun @bitkyc08/opencodex

added 102 packages in 8s

37 packages are looking for funding
  run `npm fund` for details
```

```
$ ocx --version
opencodex 2.100.2
```

npm registry自体から取得できたため、依存解決・インストールは問題なく完了した。
グローバルインストール先の`package.json`・`LICENSE`を直接確認し、MITライセンスであることを確認した
(`LICENSE`ファイル全文が標準的なMIT Licenseの文言、`Copyright (c) 2026 opencodex contributors`)。

## 2. モックバックエンドの用意とプロバイダ登録

Ollamaの代わりに、`/v1/chat/completions`(OpenAI Chat Completions互換)だけを実装した
Node.jsの最小サーバーを`localhost:11434`(Ollamaの既定ポート)で起動した。

```
$ node mock_ollama_server.js &
[mock-ollama] listening on http://localhost:11434
```

opencodexの公式ヘルプに載っている例そのままの形で、カスタムプロバイダとして登録した。

```
$ ocx provider add my-ollama --adapter openai-chat --base-url http://localhost:11434/v1 \
    --default-model mock-model --allow-private-network --auth-mode local --set-default --json
{
  "action": "added",
  "provider": "my-ollama",
  "adapter": "openai-chat",
  "baseUrl": "http://localhost:11434/v1",
  "defaultModel": "mock-model",
  "isDefault": true,
  "source": "custom",
  "needsSync": true
}
```

```
$ ocx start
   outbound proxy: http://127.0.0.1:37619/
🚀 opencodex proxy running on http://localhost:10100
   POST /v1/responses → provider translation
   POST /v1/chat/completions → OpenAI-compatible clients
   GET  /healthz      → health check
   GET  /api/*        → management API
   GET  /             → GUI dashboard
🔐 Claude intercept proxy active on http://127.0.0.1:10200 (CONNECT api.anthropic.com → local TLS)
```

## 3. 1回目の失敗: ストリーミング非対応のモックで502

最初に書いたモックサーバーは、通常のJSON(非ストリーミング)だけを返す実装だった。
その状態でAnthropic Messages API形式のリクエストをプロキシに送ると、502になった。

```
$ curl -s -X POST http://localhost:10100/v1/messages \
    -H "Content-Type: application/json" -H "x-api-key: dummy" \
    -H "anthropic-version: 2023-06-01" \
    -d '{"model":"my-ollama/mock-model","max_tokens":64,"messages":[{"role":"user","content":"..."}]}' \
    -w "\nHTTP_STATUS:%{http_code}\n"

{"type":"error","error":{"type":"overloaded_error","message":"The provider failed to complete the request."}}
HTTP_STATUS:502
```

モックサーバーのログを見ると、opencodexはバックエンドへのリクエストに`"stream":true`を
付けて転送していた(Anthropic Messages API自体はstreamを指定していないにもかかわらず)。

```
[mock-ollama] body: {"model":"mock-model","messages":[{"role":"user","content":"..."}],
"stream":true,"max_tokens":64,"stream_options":{"include_usage":true}}
```

モックサーバーがSSE(Server-Sent Events)のストリーミング応答を実装していなかったため、
opencodex側がバックエンドからの応答形式を解釈できず失敗した、という挙動だと分かった。
これはopencodexの実装上の挙動そのもの(OpenAI-compatibleバックエンドに対しては既定で
streamingを要求する)であり、Ollama本体も`/v1/chat/completions`でSSEストリーミングに
対応しているため、実機のOllamaであれば起きない問題と考えられる。

## 4. モックをSSE対応にして再検証 → 成功

モックサーバーに`stream:true`のときだけSSE形式(`data: {...}\n\n`の連続+`data: [DONE]`)で
応答するコードを追加し、同じリクエストを再送した。

```
$ curl -s -X POST http://localhost:10100/v1/messages \
    -H "Content-Type: application/json" -H "x-api-key: dummy" \
    -H "anthropic-version: 2023-06-01" \
    -d '{"model":"my-ollama/mock-model","max_tokens":64,
         "messages":[{"role":"user","content":"こんにちは、opencodex経由でAnthropic Messages API形式のリクエストを送っています。"}]}' \
    -w "\nHTTP_STATUS:%{http_code}\n"

{"id":"msg_27a3533fced24320babd65dd4e583408","type":"message","role":"assistant",
 "content":[{"type":"text","text":"Hello from the mock Ollama backend. opencodex proxied this correctly."}],
 "model":"my-ollama/mock-model","stop_reason":"end_turn","stop_sequence":null,
 "usage":{"input_tokens":0,"output_tokens":0,"cache_read_input_tokens":0,"cache_creation_input_tokens":0}}
HTTP_STATUS:200
```

Anthropic Messages API形式のリクエスト(`/v1/messages`、`x-api-key`ヘッダ、
`anthropic-version`ヘッダ)が、OpenAI Chat Completions形式のバックエンドに正しく変換されて
転送され、応答がAnthropic Messages API形式(`content`配列、`stop_reason`等)に変換し直されて
返ってきたことを確認した。

(`usage`が`0`なのは、モックサーバーがSSEチャンクに`usage`フィールドを含めなかったため。
opencodex自体のバグではなく、モック側の簡略化によるもの。)

## 5. 3つの受け口(inbound)形式すべてで確認

同じモックバックエンド・同じプロバイダ設定のまま、opencodexが対応する3つの受け口形式すべてで
リクエストを送り、いずれも200かつ各形式に応じた正しい構造の応答が返ることを確認した。

```
$ curl -s -X POST http://localhost:10100/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"my-ollama/mock-model","messages":[{"role":"user","content":"OpenAI Chat Completions形式で送信したテストです。"}]}' \
    -w "\nHTTP_STATUS:%{http_code}\n"

{"id":"chatcmpl-mock-001","object":"chat.completion","created":1794618586,"model":"mock-model",
 "choices":[{"index":0,"message":{"role":"assistant","content":"Hello from the mock Ollama backend. opencodex proxied this correctly."},"finish_reason":"stop"}],
 "usage":{"prompt_tokens":10,"completion_tokens":12,"total_tokens":22}}
HTTP_STATUS:200

$ curl -s -X POST http://localhost:10100/v1/responses \
    -H "Content-Type: application/json" \
    -d '{"model":"my-ollama/mock-model","input":"Responses API形式で送信したテストです。"}' \
    -w "\nHTTP_STATUS:%{http_code}\n"

{"id":"resp_1c0d479a8b344b00a88e5cd3e303326b","object":"response","created_at":1794618586,"status":"completed",
 "model":"mock-model","output":[{"type":"message","id":"msg_6b44431a2560487184a5149e27dce321","role":"assistant",
 "status":"completed","content":[{"type":"output_text","text":"Hello from the mock Ollama backend. opencodex proxied this correctly.","annotations":[]}],"phase":"final_answer"}],
 "usage":{"input_tokens":10,"output_tokens":12,"total_tokens":22,"input_tokens_details":{"cached_tokens":0},"output_tokens_details":{"reasoning_tokens":0}}}
HTTP_STATUS:200
```

まとめ:

| 送信した形式(inbound) | エンドポイント | 結果 |
|---|---|---|
| Anthropic Messages API | `POST /v1/messages` | ✅ 200(Anthropic形式の応答に変換済み) |
| OpenAI Chat Completions | `POST /v1/chat/completions` | ✅ 200(OpenAI Chat Completions形式の応答) |
| OpenAI Responses API | `POST /v1/responses` | ✅ 200(Responses形式の応答に変換済み) |

3形式すべてで、同じ1つのバックエンド(OpenAI Chat Completions互換)への変換・転送と、
元の形式への応答変換が機能した。これが「`provider/model`形式を指定し、ベースURLを
`http://localhost:10100/v1`に向けるだけで任意のプロバイダに接続できる」というopencodexの
核心的な価値提案にあたる部分であり、実際に動作することを確認できた。

## ライセンス・公式の免責事項

- `LICENSE`: MIT License(`Copyright (c) 2026 opencodex contributors`)。
- README「Disclaimer」節: 「opencodexは独立したコミュニティメンテナンスのプロジェクトで、
  OpenAI・Anthropic等の提供元とは無関係」「Anthropic(Claude)等は、サードパーティのプロキシ経由の
  APIトラフィックに対してアカウントを停止・制限する場合がある。自己責任(UAYOR)で利用し、
  プロバイダ接続前に利用規約でプロキシ経由アクセスが許可されているか確認すること」と明記されている。
  この記載どおり、本検証では実際のClaude Code/Codexの製品ログインは使っていない。

## スコープ外(今回やらなかったこと)

- 実際のOllamaへのルーティング(ネットワーク制約により未実施。上記の通り、Ollamaの
  `/v1/chat/completions`はSSEストリーミングに対応しているため、本検証のモックと同様に
  動作すると考えられるが、実機での確認はできていない)。
- `ocx claude`での実際のClaude Code/Codex製品ログインを通した検証(アカウントリスクを避けるため
  意図的にスコープ外とした。today.md記載の方針どおり)。
- 複数プロバイダへのフェイルオーバー/重み付きラウンドロビン(「コンボ」)機能。
