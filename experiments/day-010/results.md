# Day 010 結果ログ: REA (morluto/rea) を自作Electronアプリで検証

対象: https://github.com/morluto/rea (MIT, npm: `rea-agents`, 検証時点の最新版 `5.0.0`)

## 0. スコープ

today.md / backlog.md の制約に従い、以下に限定した。

- **検証対象は自分で書いた最小のElectronアプリ(`sample-app/`)のみ**。第三者の著作物は一切解析していない。
- **ネイティブバイナリ解析(Hopper/Ghidra/IDA)は今回は使わない。** 静的なJavaScript/Electron解析のパスだけを検証する(README記載の
  `analyze-javascript-application` は「MCP登録・Hopper・Ghidra不要、アプリを実行せずに動く」と明記されているため)。
- **MCPサーバーとしてこのセッションのClaude Codeに registerする(`rea setup`)ことはしなかった。**
  `rea setup` はこのクラウド実行環境のグローバルなエージェント設定ファイル(`/root/.claude.json` 等)を書き換える操作であり、
  本検証の目的(ツール自体の解析精度の検証)に対してリスクが見合わないため。
  代わりに `rea` CLIを直接呼び出した。これはREA自身のドキュメント(README・付属skillの `javascript-applications.md`)が
  「MCP登録もHopper/Ghidraも不要、CLIが返すEvidenceレコードをMCP経由の結果と同じ注意深さで読めばよい」と明記している
  正式なフォールバック経路であり、検証の妥当性は損なわれない。

## 1. 検証環境

```
$ node --version
v22.22.0
$ java --version
openjdk 21.0.12.1 2026-08-18
$ npx -y rea-agents@latest --version
5.0.0
```

npm版`rea-agents@5.0.0`の`engines`は `"node": "^22.19.0 || ^24.11.0 || >=26.0.0"` で、
今回の環境のNode v22.22.0は条件を満たした。

`rea doctor --json` の結果(抜粋、`rea-output/doctor.json`に全文):

```json
{
  "healthy": false,
  "scope_checks": [
    { "name": "node", "ok": true, "detail": "22.22.0" },
    { "name": "host", "ok": true, "detail": "ubuntu 24.04" },
    { "name": "hopper", "ok": false, "classification": "missing_analysis_engine" },
    { "name": "ghidra", "ok": false, "classification": "missing_analysis_engine", "detail": "GHIDRA_INSTALL_DIR is not set" },
    { "name": "ida-registration", "ok": false, "classification": "missing_analysis_engine" },
    { "name": "skill:identity", "ok": false, "classification": "config_drift" },
    { "name": "registration:claude_code", "ok": false, "classification": "config_drift", "detail": "/root/.claude.json" }
  ]
}
```

`healthy: false` だが、これは想定通り。静的JS解析というタスクに対して `scope_checks` のうち意味を持つのは
`node`/`host` のみで、どちらも `ok: true`。Hopper/Ghidra/IDA/MCP登録はこのタスクでは使わないので
`missing`/`config_drift` のままで問題ない(READMEの `rea doctor` の説明通り)。

## 2. 検証対象: 自作アプリ `sample-app/`

`experiments/day-010/sample-app/` に、わざと短い変数名(`_q`, `_h`, `_z` など)で書いた
小さなElectronアプリを自作した。ファイル構成:

```
sample-app/
├── package.json          # main: main.js, dependencies: electron
├── main.js                # Electronメインプロセス。BrowserWindow 1個、ipcMainハンドラ2個
├── preload.js              # contextBridgeで couponApi を1個公開(getQuote/getDebug の2メンバー)
├── lib/pricing.js          # クーポン割引ロジック本体(今回の「隠された機能」)
└── renderer/
    ├── index.html
    └── renderer.js
```

**このアプリの正解(筆者自身が書いたので100%わかっている)**:

`lib/pricing.js` の `_q(code, subtotal)` 関数は、`code` の各文字コードの合計を7で割った余り `m` を使って
以下の分岐で割引後の金額を返す。

| 条件 | 割引 |
|---|---|
| `code` が `VIP-` で始まり、かつ `m === 0` | 50%オフ |
| `code` が `VIP-` で始まり、`m !== 0` | 15%オフ |
| `VIP-` で始まらず、`m === 3` | 一律$10オフ |
| それ以外 | 割引なし |

加えて `main.js` には `ipcMain.handle('coupon:debug', ...)` という2つ目のIPCチャンネルがあり、
`lib/pricing.js` の `_z(e)`(`debugSnapshot`としてexport)が
**`process.env.COUPON_DEBUG === '1337'` のときだけ** 内部状態のキー一覧を返す、という
隠しデバッグ機能になっている(README/UIのどこにも説明が無い)。

実際にNodeで実行して割引ロジックの正解値を確認した:

```
$ node -e "const {quote,_hash}=require('./lib/pricing.js'); ..."
SAVE10 100 -> hash=1 price=100
VIP-GOLD 200 -> hash=4 price=170
VIP-SILVER 200 -> hash=4 price=170
WELCOME 50 -> hash=6 price=50
HELLO 30 -> hash=1 price=30
BS7PDG 100 -> hash=3 price=90      # 非VIPでhash%7==3 -> 一律$10オフの実例
VIP-D5KV9 100 -> hash=0 price=50   # VIP-でhash%7==0 -> 50%オフの実例
debug(no flag)= null
debug(flag)= {"k":["cartTotals","lastCoupons","internalHash"],"n":1791422238979}
```

この「正解」を基準に、REAの静的解析がどこまで言い当てられるかを検証する。

## 3. `analyze-javascript-application` の結果

```
$ npx -y rea-agents@latest analyze-javascript-application ./sample-app --format json \
    > rea-output/analyze-javascript-application.json
```

実行は1回で成功、終了コード0。出力は約1.3MB/37,802行のJSON(`rea-output/analyze-javascript-application.json`)。

`normalized_result.statistics`:

```json
{
  "relevant_files": 6,
  "parsed_javascript_files": 4,
  "visited_ast_nodes": 415,
  "findings": 21,
  "parse_failures": 0,
  "truncated_scopes": 0
}
```

`relevant_files: 6` はアプリの全ファイル数(`package.json`, `main.js`, `preload.js`, `lib/pricing.js`,
`renderer/index.html`, `renderer/renderer.js`)と一致。`parse_failures: 0` で全JSファイルを解析できている。

`normalized_result.summary` はアプリの構造を**完全に正確に**言い当てた。

| 項目 | REAの値 | 正解 |
|---|---|---|
| `browser_windows` | 1 | 1 (`main.js`の`_mk()`内の`new BrowserWindow`) |
| `explicit_web_preferences` | 3 | 3 (`preload`/`contextIsolation`/`nodeIntegration`) |
| `preload_entrypoints` | 1 | 1 (`preload.js`) |
| `context_bridge_apis` | 1 | 1 (`couponApi`) |
| `exposed_api_members` | 2 | 2 (`getQuote`, `getDebug`) |
| `ipc.main_handlers` | 2 | 2 (`coupon:quote`, `coupon:debug`) |

さらに `normalized_result.semantic_graph.nodes` (AST由来のexpressionノード、295個)の中に、
`lib/pricing.js` 26行目の `e.COUPON_DEBUG` という**プロパティ読み取り**が、
`confidence: "exact"`・`authority: "ast-static-analysis"`・正確なソース位置(`line 26, column 6-20`)付きで
1個のノードとして記録されていた。つまり「隠しデバッグ機能のトリガーになる文字列」自体は、
最初の1回の解析で既に生のEvidenceの中に存在していた。

## 4. `trace_application_feature` で「隠し機能」を追いかけてみる

ここからが今回の検証の核心。「REAがEvidenceを返すこと」と「REAが機能の意味を説明してくれること」は別物だと
わかったので、公式ドキュメント(skill付属の `references/javascript-applications.md`)が推奨する
`trace_application_feature` を使い、実際にどこまで追跡できるかを試した。

### 4-1. 入力形式はドキュメント化されていなかった

`--help` / `--schema` / `--llms-full` では `inputJson` の内部構造(`application`/`seed`のキー名やenum値)が
一切説明されておらず、GitHub上の `skills/reverse-engineer-anything/references/javascript-applications.md` にも
「`trace_application_feature`に`node ID, route, string, API, IPC channel, module, native export`のいずれかを渡す」
という説明はあるが、JSONのキー名までは書かれていない。

実際には、**バリデーションエラーのレスポンス自体がスキーマを明かしてくれた**。

```
$ npx -y rea-agents@latest trace-application-feature '{}' --format json
{
  "details": { "issues": [
    { "path": ["application"], "reason": "missing_argument", "expected": "object" },
    { "path": ["seed"], "reason": "missing_argument", "expected": "object" }
  ]}
}
```

```
$ npx -y rea-agents@latest trace-application-feature '{"application":<analyze結果全体>,"seed":{}}' --format json
{
  "details": { "issues": [
    { "path": ["seed","kind"], "reason": "invalid_value",
      "expected": ["node-id","route","string","api","channel","module","native-export"] },
    { "path": ["seed","value"], "reason": "missing_argument", "expected": "string" },
    { "path": ["seed","match"], "reason": "invalid_value", "expected": ["exact"] }
  ]}
}
```

この2段階のエラーメッセージから `{"application": <analyze-javascript-applicationの出力全体>, "seed": {"kind": "string", "value": "...", "match": "exact"}}`
という形が復元できた。ドキュメントを読んでもわからなかった部分を、ツール自身の失敗時レスポンスが補ってくれた、
というのも実際に手を動かしたことで分かった発見。

### 4-2. IPCチャンネル名(文字列リテラル)でのトレースは成功し、アプリ構造を正確に再構築した

```
$ npx -y rea-agents@latest trace-application-feature <seed: "coupon:debug"> --format json
```

結果(`rea-output/trace-coupon-debug-channel.json`):

```json
{
  "summary": {
    "matched_seeds": 2, "traced_nodes": 28, "traced_edges": 43,
    "terminal_paths": 0, "observed_facts": 35, "inferred_facts": 39
  }
}
```

`seed_matches` は `ipc-channel`(`coupon:debug`)と `ipc-handler`(`coupon:debug`)の2つに正確にヒットし、
返ってきた28ノードのグラフには `main.js`/`preload.js`/`lib/pricing.js`/`renderer/renderer.js` の
モジュール関係、`context-bridge-api: couponApi`、`browser-window`、両方のIPCチャンネル
(`coupon:quote`と`coupon:debug`)がすべて正しく含まれていた。アプリの「配線」の再構築はここまで正確だった。

### 4-3. しかし「なぜ隠し機能なのか」までは自動では繋がらなかった

同じトレース結果で `"terminal_paths": 0`、`"paths": []`。つまり `coupon:debug` チャンネルから
「`process.env.COUPON_DEBUG === '1337'` というゲート条件を通る」という具体的な経路(path)は
**1回のトレース呼び出しでは返ってこなかった**。3節で見つけた `COUPON_DEBUG` のEvidenceノードと
`coupon:debug` ハンドラーを結びつけるには、返ってきた生のEvidence(semantic_graph)を自分で読んで
`function_node_id` を手がかりに該当する関数本体を探す、という一手が別途必要だった。

さらに、識別子そのもの(`"COUPON_DEBUG"`、`"quote"`、`"debugSnapshot"`、`"VIP-"`)をseedの`value`に
指定した場合は、いずれも以下のように **"no-match"** になった。

```json
{ "coverage": { "status": "no-match", "total_seed_matches": 0 },
  "limitations": ["No graph entity matched the literal seed; this is not evidence that the feature is absent."] }
```

`trace_application_feature` の`kind: "string"`は「AST上の**文字列リテラル値**(IPCチャンネル名など)」を
指しており、変数名・プロパティ名そのもの(識別子)は拾わない、という挙動がここでわかった。
ネイティブバイナリ解析用の `search` コマンドで文字列/プロシージャ名を横断検索できるが、これはJS/Electron
ディレクトリには使えない(`target_unavailable: "This target is a directory..."`というエラーで確認済み、
`rea-output/search-coupon-debug.json`参照)。つまり**JS解析では「全文字列・識別子の横断検索」に相当する
CLIコマンドが現時点では無く**、未知の識別子を手当たり次第investigateする手段は無かった。

## 5. 広告されている機能の一部は外部ツール前提で、今回の環境では動かなかった

`recover-javascript-sources`(「読みやすいJSモジュールを復元する」機能)を試したところ、失敗した。

```
$ npx -y rea-agents@latest recover-javascript-sources ./sample-app ./rea-output/recovered --format json
{
  "code": "capability_unavailable",
  "category": "unsupported_provider",
  "details": {
    "provider_id": "wakaru",
    "reason": "Provide an absolute REA_WAKARU_COMMAND pointing to Wakaru 1.13.0 on Linux x64; no tool is installed by REA"
  }
}
```

READMEのトップレベルの説明では「Hopper/Ghidraはネイティブ解析にのみ必要、静的JS解析はどちらも不要」と
明記されているが、**「読みやすいソースの復元」という機能は別の外部ツール(Wakaru)がさらに必要**で、
これはREAが自動インストールしない前提になっている。今回はこの経路を深追いしなかった(スコープ外)。
`analyze-javascript-application`自体は外部ツール無しで動いた(2節参照)ので、
「静的解析でEvidenceを取る」部分と「読みやすいソースに変換する」部分は別の依存関係を持つ、
という点は今回動かして初めてわかった。

## 6. まとめ: 「どこまで正確に説明できたか」

- ✅ **アプリの構造(IPC配線・contextBridge公開API・BrowserWindow設定)は100%正確に再構築できた。**
  カウント値はすべて正解と一致し、ソース位置も1行単位で正確だった。
- ✅ **「隠しデバッグチャンネルが存在する」という事実自体は、最初の1回の解析で既にEvidenceの中に
  (`COUPON_DEBUG`の読み取りノードとして)存在していた。**
- ⚠️ **「なぜそれが隠し機能なのか(どの環境変数のどの値でゲートされているか)」という1文の説明は
  自動では出てこず、Evidenceグラフを自分で(または人間/エージェントが)読んで繋ぐ必要があった。**
  README/宣伝文句の「See a feature you like. Understand how it works, down to the binary level.」は、
  「ツールが勝手に説明文を書いてくれる」という意味ではなく、「説明に必要な正確なEvidenceを揃えてくれる」
  という意味だと理解するのが正確、というのが実際に動かして得た結論。
- ⚠️ **割引ロジックの4分岐(VIP-判定・hash%7の分岐)についても同様。** `analyze-javascript-application`は
  変数名・AST構造・コードフローを変えずに正確に保持するので、今回のように短い変数名程度の「軽い難読化」
  であれば人間が`lib/pricing.js`を読めば10分もかからず正解に到達できる。ただし今回のREAのツール群
  (`trace_application_feature`など)は、そこまでの要約・説明は自動生成せず、「正確な断片的事実」を
  返すところで止まる、という設計だと確認できた。

## 7. 日本語記事の有無(再確認)

2026-10-08時点であらためて確認。Zenn/Qiita/noteで「REA」「rea-agents」「morluto/rea」での日本語紹介記事は
検索した範囲で確認できず、backlog.mdの記載(0件、2026-10-07時点)から変化なし。
