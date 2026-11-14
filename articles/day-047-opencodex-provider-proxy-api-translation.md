---
title: "opencodexでAnthropic/OpenAI形式のリクエストをローカルのQwen2.5-32Bに流してみた"
emoji: "🔌"
type: "tech"
topics: ["ai", "llm", "ollama", "anthropic", "openai"]
published: false
---

## これは何を試した記事か

[lidge-jun/opencodex](https://github.com/lidge-jun/opencodex)(npm: `@bitkyc08/opencodex`、MIT)は、OpenAI Codex・Claude Code・Claude Desktop等のコーディングエージェントと、Claude/Gemini/Grok/DeepSeek/ローカルOllama等の各モデルプロバイダーの間に立つローカルゲートウェイである。
GitHub TrendingのTypeScript部門で1日+55starを集めていた。

売りは、Anthropic Messages API・OpenAI Chat Completions API・OpenAI Responses APIという3つのAPI形式を相互変換し、エージェント側のベースURLを`http://localhost:10100/v1`に向けるだけで任意のプロバイダに接続できる点である。
本記事では、この変換を手元のOllamaで動かしたQwen2.5-32Bに対して実際に通し、テキスト応答・ストリーミング・ツール呼び出しまで正しく変換されるかを確かめた。

結論を先に書くと、3形式すべてで変換は正しく機能し、ストリーミングとツール呼び出しの往復も動いた。
プロキシを挟むことによる遅延は測れるほど無かった。
一方で、Anthropic形式の応答だけ`model`フィールドが`"the requested model"`という文字列に置き換わる挙動を見つけた。
原因はOllamaのモデル名に含まれる`:`だった。

- 出典: https://github.com/lidge-jun/opencodex (MIT、検証時バージョン `2.100.2`)
- 日本語記事件数(2026-11-13時点、Zenn/Qiita/note検索): 0件

## 検証環境とモデルの選び方

| 項目 | 内容 |
|---|---|
| OS | Windows + WSL2 |
| CPU / RAM | AMD Ryzen 7 7700 / 30GiB |
| GPU | NVIDIA GeForce RTX 5060 Ti 16GB |
| Node.js / npm | v26.8.2 / 11.19.1 |
| Ollama | 0.35.1 |
| モデル | qwen2.5:32b-instruct(Q4_K_M、19GB) |

モデルは、このPCで動かせる最大サイズを選んだ。
VRAM 16GBとRAM 30GiBの組み合わせでは、32BのQ4(約20GB)がVRAMとRAMに分割して載るのが上限で、70B級(Q4で40GB超)はRAMにも収まらない。

```bash
$ ollama pull qwen2.5:32b-instruct
success
$ ollama ps
NAME                    ID              SIZE     PROCESSOR          CONTEXT
qwen2.5:32b-instruct    9f13ba1299af    21 GB    30%/70% CPU/GPU    4096
```

3割がCPU側に載るため、生成速度は約6.2 tok/sだった。

## スコープ: 製品アカウントは使わない

opencodex公式READMEの「Disclaimer」節には、次のように明記されている。

> Some providers — notably Anthropic (Claude) — may suspend or restrict accounts that route API traffic through third-party proxies. **Use at your own risk (UAYOR).**

このため本検証では、Claude Code/Codexの製品アカウント(サブスクリプションログイン)は使わず、各API形式のリクエストをcurlで直接プロキシに送って変換を確かめた。
バックエンドは手元のOllamaだけなので、外部のプロバイダには一切通信していない。

## インストールと、HOMEを分けて起動した理由

グローバルではなく、作業ディレクトリにインストールした。

```bash
$ npm install --loglevel=error @bitkyc08/opencodex@2.100.2
found 0 vulnerabilities
$ ./node_modules/.bin/ocx --version
opencodex 2.100.2
```

インストール先の`LICENSE`がMIT Licenseであることを確認した。

起動する前にソースを読むと、opencodexにはClaude Code/Claude Desktopとの連携のために`~/.claude/settings.json`へ`HTTPS_PROXY`や`NODE_EXTRA_CA_CERTS`を書き込む処理や、Codexの`~/.codex/config.toml`を書き換える処理が含まれていた。
筆者のPCではClaude Codeを普段使いしているので、環境変数`HOME`を作業用のディレクトリに向けて隔離した状態で動かした。

```bash
$ W=~/work-day047
$ HOME=$W/home ocx provider add my-ollama --adapter openai-chat \
    --base-url http://localhost:11434/v1 --default-model qwen2.5:32b-instruct \
    --allow-private-network --auth-mode local --set-default --json
{
  "action": "added",
  "provider": "my-ollama",
  "adapter": "openai-chat",
  "baseUrl": "http://localhost:11434/v1",
  "defaultModel": "qwen2.5:32b-instruct",
  "isDefault": true,
  ...
}

$ HOME=$W/home ocx start
🚀 opencodex proxy running on http://localhost:10100
   POST /v1/responses → provider translation
   POST /v1/chat/completions → OpenAI-compatible clients
🔐 Claude intercept proxy active on http://127.0.0.1:10200 (CONNECT api.anthropic.com → local TLS)
  ℹ️  Anonymous telemetry is awaiting human consent (run 'ocx telemetry status' or open the dashboard; disable anytime with 'ocx telemetry disable' or OCX_TELEMETRY=0).
```

設定ファイルは隔離先の`.opencodex/`に作られ、本物の`~/.claude/settings.json`は検証の前後で変わっていなかった(sha256で確認)。
`ocx start`は何もしなくても`api.anthropic.com`向けの通信を横取りするための「Claude intercept proxy」を立ち上げる点と、匿名テレメトリが同意待ちで起動する点は、試す前に知っておいたほうがよい。
テレメトリには同意していない。

## 3つの受け口すべてで32Bに変換・転送できた

同じ質問を3つの形式で送った。

```bash
$ curl -s -X POST http://localhost:10100/v1/messages \
    -H "Content-Type: application/json" -H "x-api-key: dummy" -H "anthropic-version: 2023-06-01" \
    -d '{"model":"my-ollama/qwen2.5:32b-instruct","max_tokens":128,
         "messages":[{"role":"user","content":"日本の首都はどこですか?理由を1文で添えて、日本語で答えてください。"}]}'
{"type":"message","role":"assistant","content":[{"type":"text","text":"日本の首都は東京です。…"}],
 "model":"the requested model","stop_reason":"end_turn",
 "usage":{"input_tokens":26,"output_tokens":116,"cache_read_input_tokens":24,"cache_creation_input_tokens":0}}
HTTP_STATUS:200

$ curl -s -X POST http://localhost:10100/v1/chat/completions -H "Content-Type: application/json" \
    -d '{"model":"my-ollama/qwen2.5:32b-instruct","messages":[{"role":"user","content":"(同じ質問)"}]}'
{"object":"chat.completion","model":"qwen2.5:32b-instruct",
 "choices":[{"index":0,"message":{"role":"assistant","content":"日本の首都は東京です。これは、日本国憲法と国家の行政中心地であるという実情に基づいています。"},"finish_reason":"stop"}],
 "usage":{"prompt_tokens":50,"prompt_tokens_details":{"cached_tokens":49},"completion_tokens":29,"total_tokens":79}}
HTTP_STATUS:200

$ curl -s -X POST http://localhost:10100/v1/responses -H "Content-Type: application/json" \
    -d '{"model":"my-ollama/qwen2.5:32b-instruct","input":"(同じ質問)"}'
{"object":"response","status":"completed","model":"qwen2.5:32b-instruct",
 "output":[{"type":"message","role":"assistant","content":[{"type":"output_text","text":"日本の首都は東京です。…"}]}],
 "usage":{"input_tokens":50,"output_tokens":110,"total_tokens":160,"input_tokens_details":{"cached_tokens":49}}}
HTTP_STATUS:200
```

| 送信した形式 | エンドポイント | 結果 |
|---|---|---|
| Anthropic Messages API | `POST /v1/messages` | ✅ 200(`content`配列・`stop_reason`) |
| OpenAI Chat Completions | `POST /v1/chat/completions` | ✅ 200(`choices[].message`) |
| OpenAI Responses API | `POST /v1/responses` | ✅ 200(`output[].content[].output_text`) |

細かいところまで変換されていた。
Anthropic形式の`usage`を見ると、Ollama側が返したキャッシュ済みトークン数が`cache_read_input_tokens`に振り分けられていて、`input_tokens`の26と合わせるとOpenAI形式の`prompt_tokens`の50に一致した。

なお、Anthropic形式とResponses形式の回答には、日本語の途中で中国語の文が混ざるものがあった(例: 「日本の首都は東京です。这是因为自1868年以来…」)。
プロキシを通さずにOllamaへ直接送った場合でも同じことが起きたので、これはQwen2.5-32Bの出力の性質で、opencodexの変換とは関係がない。

## ストリーミングもAnthropicのイベント形式で返る

`"stream":true`を付けてAnthropic形式で送ると、Anthropic APIと同じSSEのイベント列に変換されて返ってきた。

```bash
$ curl -s -N -X POST http://localhost:10100/v1/messages ... \
    -d '{"model":"my-ollama/qwen2.5:32b-instruct","max_tokens":64,"stream":true,
         "messages":[{"role":"user","content":"1から5まで数字だけをカンマ区切りで。"}]}' \
  | grep '^event:' | sort | uniq -c
      9 event: content_block_delta
      1 event: content_block_start
      1 event: content_block_stop
      1 event: message_delta
      1 event: message_start
      1 event: message_stop
      1 event: ping
```

`content_block_delta`のテキストをつなげると`1,2,3,4,5`になった。

## ツール呼び出しも往復で変換できた

コーディングエージェントで本当に重要なのは、テキストよりもツール呼び出しの変換である。
Anthropic形式で`get_weather`というツールを定義して、「東京の今の天気を調べて。」と送った。

```bash
$ curl -s -X POST http://localhost:10100/v1/messages ... \
    -d '{"model":"my-ollama/qwen2.5:32b-instruct","max_tokens":256,
         "tools":[{"name":"get_weather","description":"Get the current weather for a city",
                   "input_schema":{"type":"object","properties":{"city":{"type":"string","description":"City name in English"}},"required":["city"]}}],
         "messages":[{"role":"user","content":"東京の今の天気を調べて。"}]}'
{"type":"message","role":"assistant",
 "content":[{"type":"tool_use","id":"call_ddztmfzd","name":"get_weather","input":{"city":"Tokyo"}}],
 "stop_reason":"tool_use", ...}
```

Ollama側ではOpenAI形式の`tool_calls`として扱われているはずのものが、Anthropic形式の`tool_use`ブロックとして返ってきた。
この`tool_use`のIDに対して`tool_result`を返した。

```bash
$ curl -s -X POST http://localhost:10100/v1/messages ... \
    -d '{ ..., "messages":[
          {"role":"user","content":"東京の今の天気を調べて。"},
          {"role":"assistant","content":[{"type":"tool_use","id":"call_ddztmfzd","name":"get_weather","input":{"city":"Tokyo"}}]},
          {"role":"user","content":[{"type":"tool_result","tool_use_id":"call_ddztmfzd",
                                     "content":"{\"city\":\"Tokyo\",\"condition\":\"rain\",\"temp_c\":14}"}]}]}'
{"content":[{"type":"text","text":"現在、東京の天気は雨で、気温は14℃です。"}],"stop_reason":"end_turn", ...}
HTTP_STATUS:200
```

ツールの結果を使った回答が返り、往復の変換が機能した。
Responses API形式の`function`ツールでも、`function_call`として正しく返ってきた。

```json
"output":[{"type":"function_call","call_id":"call_h96xqhfe","name":"get_weather",
           "arguments":"{\"city\":\"東京\"}","status":"completed"}]
```

## プロキシを挟んでも遅くならない

temperature 0・最大32トークンで同じリクエストを、Ollamaへの直接送信とopencodex経由とで3回ずつ交互に送った。

```bash
$ ./overhead.sh
run1  direct 5.708604s (32 tok)   via-opencodex 5.208805s (32 tok)
run2  direct 5.226990s (32 tok)   via-opencodex 5.256594s (32 tok)
run3  direct 5.304535s (32 tok)   via-opencodex 5.241122s (32 tok)
```

差はばらつきの範囲に収まっており、プロキシによる遅延は測れるほどではなかった。
32Bモデルの生成自体が約6 tok/sなので、変換処理のコストはそれに比べて無視できる。

## 見つけた挙動: Anthropic形式だけ `model` が "the requested model" になる

上の結果をよく見ると、Anthropic形式の応答だけ`model`フィールドが`"the requested model"`という文字列になっている。
Chat Completions形式とResponses形式では`qwen2.5:32b-instruct`が入っていた。
ストリーミングの`message_start`イベントでも同じだった。

ソースを追うと、原因は`src/lib/error-destination.ts`の`clientFacingModelLabel`にあった。
クライアントに見せるモデル名を次の正規表現で検証し、合わない場合はプレースホルダーに置き換えている。

```ts
const clientModelId = /^[A-Za-z0-9][A-Za-z0-9._-]*(?:\/[A-Za-z0-9][A-Za-z0-9._-]*){0,3}$/;
```

この正規表現は`:`を許可していないので、Ollamaのタグ付きのモデル名(`qwen2.5:32b-instruct`)は弾かれる。
`ollama cp`でコロンの無い別名を作って確かめた。

```bash
$ ollama cp qwen2.5:32b-instruct qwen32b
copied 'qwen2.5:32b-instruct' to 'qwen32b'
## model=my-ollama/qwen2.5:32b-instruct
  model field: 'the requested model'
## model=my-ollama/qwen32b
  model field: 'my-ollama/qwen32b'
```

コロンの無い名前なら、リクエストしたモデル名がそのまま返ってきた。
応答本文やツール呼び出しには影響しないが、`model`を表示・記録するクライアントでは、どのモデルが答えたのかが分からなくなる。
Ollamaのモデル名はほぼすべて`名前:タグ`の形なので、Ollamaと組み合わせる場合は踏みやすい挙動である。

## ライセンスと利用上の注意

- `LICENSE`: MIT License(`Copyright (c) 2026 opencodex contributors`)。
- README「Disclaimer」節: opencodexは独立したコミュニティメンテナンスのプロジェクトで、OpenAI・Anthropic等の提供元とは無関係。Anthropic等が非公式プロキシ経由のアカウントを停止・制限する可能性があると明記されている。
- 使用モデル: Qwen2.5-32B-Instruct(Apache-2.0)。

## まとめ

- 手元のOllamaで動かしたQwen2.5-32Bに対し、Anthropic Messages・OpenAI Chat Completions・OpenAI Responsesの3形式すべてで変換・転送が機能した。
- Anthropic形式のストリーミングは正規のSSEイベント列で返り、ツール呼び出しは`tool_use`→`tool_result`の往復とResponses形式の`function_call`の両方で変換できた。
- プロキシを挟むことによる遅延は、ばらつきの範囲に収まって測れなかった。
- Anthropic形式の応答だけ、`model`フィールドがOllamaのモデル名に含まれる`:`のせいで`"the requested model"`に置き換わる。
- `ocx start`は既定で`api.anthropic.com`向けの横取り用プロキシも起動し、ソースには`~/.claude/settings.json`を書き換える処理もある。Claude Codeを普段使いしているPCで試すなら、HOMEを分けて動かすのが安心だった。

コーディングエージェントのAPI形式の違いを吸収してローカルモデルにつなぐ、という中心の機能は、32Bの実モデル相手でもツール呼び出しまで含めて素直に動いた。
ただ、手元の設定を書き換えたり通信を横取りしたりする機能も同じツールに入っているので、何が起動するのかを把握してから使うのがよいと感じた。
