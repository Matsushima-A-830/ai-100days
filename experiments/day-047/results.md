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

---

## ローカル検証(2026-11-14, 人間のPC・実機Ollama)

Routine実行環境ではモックサーバーで代替した部分を、実機のOllamaで追試した。
モデルは「このPCで動かせる最大サイズ」として `qwen2.5:32b-instruct`(Q4_K_M、19GB)を新規に取得して使った。

### 環境

- OS: Windows + WSL2 / CPU: AMD Ryzen 7 7700 / RAM 30GiB / GPU: RTX 5060 Ti 16GB
- Node v26.8.2 / npm 11.19.1 / Ollama 0.35.1
- opencodex 2.100.2(PRと同じバージョンを指定。npm上の最新は2.100.3だった)

モデルサイズの選定: VRAM 16GB + RAM 30GiBでは、32BのQ4(約20GB)がVRAMとRAMに分割して載る上限。
70B級(Q4で40GB超)はRAMにも収まらないため対象外とした。
実際の配置は `ollama ps` で `21 GB  30%/70% CPU/GPU`、生成速度は約6.2 tok/s(Ollamaネイティブ計測)だった。

### インストール(グローバルではなく作業ディレクトリにローカルインストール)

```
$ npm install --loglevel=error @bitkyc08/opencodex@2.100.2
found 0 vulnerabilities
elapsed 20.49 s
$ ./node_modules/.bin/ocx --version
opencodex 2.100.2
```

### HOMEを分離して起動した理由

ソースを確認すると、opencodexにはClaude Code/Claude Desktop連携のために `~/.claude/settings.json` に
`HTTPS_PROXY` / `NODE_EXTRA_CA_CERTS` を書き込む処理(`src/claude/desktop-system-proxy.ts` 等)や、
Codexの `~/.codex/config.toml` を書き換える処理がある。
また `ocx start` は既定で「Claude intercept proxy」(`127.0.0.1:10200`、`CONNECT api.anthropic.com → local TLS`)も起動する。
このPCではClaude Codeを普段使いしているため、`HOME=~/work-day047/home` として隔離した状態でocxを実行した
(設定は `~/work-day047/home/.opencodex/` に作られた。本物の `~/.claude/settings.json` のsha256が検証前後で変わっていないことも確認)。

```
$ HOME=$W/home ocx provider add my-ollama --adapter openai-chat --base-url http://localhost:11434/v1 \
    --default-model qwen2.5:32b-instruct --allow-private-network --auth-mode local --set-default --json
{ "action": "added", "provider": "my-ollama", "adapter": "openai-chat",
  "baseUrl": "http://localhost:11434/v1", "defaultModel": "qwen2.5:32b-instruct", "isDefault": true, ... }

$ HOME=$W/home ocx start
🚀 opencodex proxy running on http://localhost:10100
🔐 Claude intercept proxy active on http://127.0.0.1:10200 (CONNECT api.anthropic.com → local TLS)
  ℹ️  Anonymous telemetry is awaiting human consent (run 'ocx telemetry status' or open the dashboard; disable anytime with 'ocx telemetry disable' or OCX_TELEMETRY=0).
```

匿名テレメトリは同意待ちの状態で起動し、同意はしていない。

### 1. 3つの受け口すべてで実機Ollama(32B)に変換・転送(`local/run-32b.log`)

質問: `日本の首都はどこですか?理由を1文で添えて、日本語で答えてください。`

| 受け口 | HTTP | 応答の形式 | usage | 所要 |
|---|---|---|---|---|
| `POST /v1/messages`(Anthropic) | 200 | `content[].text`, `stop_reason:"end_turn"` | input 26 + cache_read 24 / output 116 | 16.80s |
| `POST /v1/chat/completions`(OpenAI) | 200 | `choices[].message` | prompt 50 / completion 29 | 4.80s |
| `POST /v1/responses`(Responses) | 200 | `output[].content[].output_text` | input 50 / output 110 | 17.96s |
| (比較)Ollama直接 `/v1/chat/completions` | 200 | — | prompt 50 / completion 32 | 5.25s |

- 所要時間の差は出力トークン数の差(29〜116トークン)による。
- Anthropic形式では、Ollamaの `prompt_tokens_details.cached_tokens` が `cache_read_input_tokens` に変換されていた(26+24=50でOpenAI側のprompt 50と一致)。
- 応答本文: Anthropic形式・Ollama直接の両方で、日本語の回答に中国語の文が混ざった(例: 「日本の首都は東京です。这是因为自1868年以来…」)。
  プロキシを通さないOllama直接でも起きているので、Qwen2.5-32Bの出力の性質であり、opencodexの変換とは無関係。

### 2. Anthropic形式のストリーミング(`local/anthropic_stream_32b.txt`)

`"stream":true` で送ると、Anthropicの正規のSSEイベント列に変換されて返った。

```
      9 event: content_block_delta
      1 event: content_block_start
      1 event: content_block_stop
      1 event: message_delta
      1 event: message_start
      1 event: message_stop
      1 event: ping
連結したtext: 1,2,3,4,5
```

### 3. ツール呼び出しの変換

Anthropic形式の `tools`(`get_weather`)を付けて「東京の今の天気を調べて。」と送った。

```
{"type":"message","role":"assistant",
 "content":[{"type":"tool_use","id":"call_ddztmfzd","name":"get_weather","input":{"city":"Tokyo"}}],
 "stop_reason":"tool_use", ...}
```

この `tool_use` に対して `tool_result`(`{"city":"Tokyo","condition":"rain","temp_c":14}`)を返すと、結果を使った回答が返った。

```
{"content":[{"type":"text","text":"現在、東京の天気は雨で、気温は14℃です。"}],"stop_reason":"end_turn", ...}
HTTP_STATUS:200
```

Responses API形式の `function` ツールでも `function_call` に変換された。

```
"output":[{"type":"function_call","call_id":"call_h96xqhfe","name":"get_weather","arguments":"{\"city\":\"東京\"}","status":"completed"}]
```

Anthropic形式のtool_use → OpenAI形式のtool_calls → Ollama、と、その逆方向の変換(tool_result → toolメッセージ)が往復で機能した。

### 4. プロキシのオーバーヘッド(`local/overhead-32b.log`)

temperature 0・max_tokens 32で同じリクエストを、Ollama直接とopencodex経由(どちらも `/v1/chat/completions`)で3回ずつ交互に送った。

```
run1  direct 5.708604s (32 tok)   via-opencodex 5.208805s (32 tok)
run2  direct 5.226990s (32 tok)   via-opencodex 5.256594s (32 tok)
run3  direct 5.304535s (32 tok)   via-opencodex 5.241122s (32 tok)
--- ollama native eval rate (32B)
eval 64 tok in 10.26s = 6.2 tok/s
```

差はばらつきの範囲内で、プロキシを挟むことによる遅延は測れるほどではなかった。

### 5. Anthropic形式の応答で `model` が "the requested model" になる

Anthropic形式の応答(非ストリーミング・ストリーミングの `message_start` とも)では、`model` フィールドが
リクエストしたモデル名ではなく `"the requested model"` という文字列になっていた
(Chat Completions・Responses形式では `qwen2.5:32b-instruct` が入っている)。

```
## model=my-ollama/qwen2.5:32b-instruct
  model field: 'the requested model'
## model=my-ollama/qwen32b            (ollama cp で作ったコロン無しの別名)
  model field: 'my-ollama/qwen32b'
```

原因は `src/lib/error-destination.ts` の `clientFacingModelLabel` で、モデル名の検証用正規表現
`/^[A-Za-z0-9][A-Za-z0-9._-]*(?:\/[A-Za-z0-9][A-Za-z0-9._-]*){0,3}$/` が `:` を許可していないため、
Ollamaのタグ付きモデル名(`qwen2.5:32b-instruct`)はプレースホルダーに置き換えられる。
Routine検証のモック(`mock-model`)はコロンを含まないため、この挙動は表に出なかった。
応答本文やツール呼び出しには影響しないが、`model` を表示・記録するクライアントでは実際のモデル名が分からなくなる。

### Routine検証(モック)との差分

- 3形式すべてで200・各形式の正しい構造に変換される点は、実機Ollamaでも同じだった。
- モックでは0だった `usage` に、実際のトークン数(キャッシュ分の内訳を含む)が入った。
- モックでは見えなかった差分として、Anthropic形式の `model` フィールドの置き換え(上記5)が見つかった。
- ストリーミング・ツール呼び出しの変換はRoutine検証では未確認だったが、実機で動作を確認した。
