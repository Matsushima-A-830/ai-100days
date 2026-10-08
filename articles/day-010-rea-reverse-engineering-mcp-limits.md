---
title: "「Reverse Engineer Anything」を名乗るMCPサーバーREAを自作Electronアプリで試した"
emoji: "🔍"
type: "tech"
topics: ["ai", "mcp", "electron", "javascript", "reverseengineering"]
published: false
---

## 要約

GitHub Trendingで急伸していた [morluto/rea](https://github.com/morluto/rea)(MITライセンス、npm: `rea-agents`、検証時点の最新版`5.0.0`)は、コーディングエージェントにネイティブバイナリ・Electron/JSアプリ・.NETアセンブリなどを解析させ「機能の挙動を調査する」ためのCLI/MCPサーバーである。

筆者はこのツールを、**自分で書いた最小のElectronアプリ(割引ロジック+隠しデバッグ機能つき)**を対象に実際に動かし、「どこまで正確に機能を説明できるか」を、正解をあらかじめ知っている状態で検証した。

結論を先に書くと、**アプリの構造(IPC配線・公開API・ウィンドウ設定)の再構築は数値レベルで完全に正確**だったが、**「なぜそれが隠し機能なのか」という1文の説明までは自動では出てこず**、返ってきたEvidence(構造化された事実の集合)を自分で読んで繋ぐ必要があった。宣伝文句の「Reverse Engineer Anything」は「ツールが説明文を書いてくれる」という意味ではなく、「説明に必要な正確な事実を揃えてくれる」という意味だと理解するのが実態に近い。

## 出典

- リポジトリ: https://github.com/morluto/rea (MIT License)
- npmパッケージ: https://www.npmjs.com/package/rea-agents (検証時点のdist-tag `latest` は `5.0.0`)
- GitHub Trending TypeScript (2026-10-07時点で本日+4,666star、14,340star)

日本語記事件数は2026-10-08時点で確認した範囲でZenn/Qiita/note共に0件だった。

## なぜこの検証スコープにしたか

REAは「ネイティブバイナリ(Mach-O/ELF/PE)・Electron/JSアプリ・.NETアセンブリ・Android APK」まで幅広く対応すると謳っているが、ネイティブバイナリ解析には別途Hopper/Ghidra/IDAのいずれかが必要になる。今回は以下の理由で**静的JavaScript/Electron解析のみ**に絞った。

- 無料OSSのGhidra(JDK21+)は検証環境に用意できたが、ネイティブバイナリ解析まで含めると半日では終わらない。
- REA自身のREADMEが「静的JS解析はMCP登録・Hopper・Ghidra不要、アプリを実行せずに動く」と明記しており、この経路だけでも「エージェントがどこまで正確に機能を説明できるか」という検証の軸は十分に検証できる。
- 第三者の著作物を無断解析するリスクを避けるため、検証対象は**筆者が自分で書いた**最小のアプリに限定した。

また、`rea setup`(MCPサーバーとしてエージェントに登録するコマンド)は、このセッションのグローバルなエージェント設定ファイルを書き換える操作のため実行しなかった。代わりに、REA自身のドキュメントが「MCP登録不要の正式なフォールバック」として明記している`rea` CLIの直接呼び出しを使った。

## 検証対象: 割引ロジック+隠しデバッグ機能を持つ自作Electronアプリ

`experiments/day-010/sample-app/` に、わざと短い変数名(`_q`, `_h`, `_z`)で書いた小さなElectronアプリを用意した。

```js
// lib/pricing.js(実際のファイルそのまま)
function _h(a) {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a.charCodeAt(i);
  return s % 7;
}

function _q(a, b) {
  const m = _h(a);
  let r;
  if (a.indexOf('VIP-') === 0 && m === 0) {
    r = b * 0.5;
  } else if (a.indexOf('VIP-') === 0) {
    r = b * 0.85;
  } else if (m === 3) {
    r = b - 10;
  } else {
    r = b;
  }
  if (r < 0) r = 0;
  return Math.round(r * 100) / 100;
}

function _z(e) {
  if (e.COUPON_DEBUG !== '1337') return null;
  return { k: ['cartTotals', 'lastCoupons', 'internalHash'], n: Date.now() };
}
```

筆者自身が書いたので正解がわかっている。クーポンコードの文字コード合計を7で割った余り`m`によって、「`VIP-`で始まり`m===0`なら50%オフ」「`VIP-`で始まり`m!==0`なら15%オフ」「`VIP-`で始まらず`m===3`なら一律$10オフ」「それ以外は割引なし」という4分岐。さらに`main.js`には`ipcMain.handle('coupon:debug', ...)`という、`process.env.COUPON_DEBUG === '1337'`のときだけ内部状態を返す**隠しデバッグチャンネル**も仕込んだ。UIのどこにも説明が無い、という想定のテストケースである。

実際にNodeで実行して正解を確認した。

```
$ node -e "const {quote,_hash}=require('./lib/pricing.js'); ..."
SAVE10 100 -> hash=1 price=100
VIP-GOLD 200 -> hash=4 price=170
BS7PDG 100 -> hash=3 price=90      # 非VIPでhash%7==3 -> 一律$10オフ
VIP-D5KV9 100 -> hash=0 price=50   # VIP-でhash%7==0 -> 50%オフ
debug(no flag)= null
debug(flag)= {"k":["cartTotals","lastCoupons","internalHash"],"n":1791422238979}
```

## `analyze-javascript-application`: 構造の再構築は完全に正確だった

```
$ npx -y rea-agents@latest analyze-javascript-application ./sample-app --format json \
    > rea-output/analyze-javascript-application.json
```

1回の実行で成功(終了コード0)。返ってきたのは約1.3MB/37,802行のJSONで、ファイル単位のASTレベルの事実(関数・変数・パラメータ・正確なソース位置・confidence)が詰まっている。

アプリの構造を表す集計値は、すべて正解と一致した。

| 項目 | REAの値 | 正解 |
|---|---|---|
| BrowserWindow数 | 1 | 1 |
| 明示的なwebPreferences数 | 3 | 3(`preload`/`contextIsolation`/`nodeIntegration`) |
| preloadエントリポイント数 | 1 | 1 |
| contextBridge API数 | 1 | 1(`couponApi`) |
| 公開APIメンバー数 | 2 | 2(`getQuote`/`getDebug`) |
| IPCハンドラー数 | 2 | 2(`coupon:quote`/`coupon:debug`) |

さらに、隠しデバッグ機能のトリガーになる`e.COUPON_DEBUG`というプロパティ読み取りも、`confidence: "exact"`・正確なソース行番号つきで、最初の1回の解析結果の中に既に記録されていた。

## `trace_application_feature`: IPCチャンネル名からの追跡は成功、だが「意味」は繋がらなかった

REA付属のskillドキュメントが推奨する`trace_application_feature`を使い、「`coupon:debug`チャンネルがどう使われているか」を追跡してみた。

まず、入力JSONの形式がCLIの`--help`/`--schema`/`--llms-full`のどこにも書かれていなかった。空オブジェクトを渡してバリデーションエラーのメッセージを読む、という手順を2回繰り返すことで、`{"application": <analyze結果全体>, "seed": {"kind": "string", "value": "coupon:debug", "match": "exact"}}`という形を特定できた。ドキュメントで分からなかった部分を、ツール自身の失敗時レスポンスが教えてくれた形になる。

この形で実行すると、`coupon:debug`という文字列リテラルから`ipc-channel`と`ipc-handler`の2件に正確にヒットし、返ってきた28ノードのグラフには`main.js`/`preload.js`/`lib/pricing.js`/`renderer/renderer.js`のモジュール関係、`couponApi`というcontext-bridge API、BrowserWindow、両方のIPCチャンネルがすべて正しく含まれていた。

```json
{
  "summary": {
    "matched_seeds": 2, "traced_nodes": 28, "traced_edges": 43,
    "terminal_paths": 0, "observed_facts": 35, "inferred_facts": 39
  }
}
```

ただし`"terminal_paths": 0`、`"paths": []`。つまり「`coupon:debug`チャンネルが`process.env.COUPON_DEBUG === '1337'`というゲート条件を通る」という具体的な経路は、この1回のトレース呼び出しでは返ってこなかった。先ほどのEvidenceの中にあった`COUPON_DEBUG`ノードと`coupon:debug`ハンドラーを結びつけるには、生のEvidence(semantic_graph)を自分で読んで関数本体を探す、という一手が別途必要だった。

さらに興味深かったのは、識別子そのもの(`"COUPON_DEBUG"`、`"quote"`、`"debugSnapshot"`、`"VIP-"`)をseedに指定すると、すべて`"no-match"`になった点だ。

```json
{ "coverage": { "status": "no-match" },
  "limitations": ["No graph entity matched the literal seed; this is not evidence that the feature is absent."] }
```

`trace_application_feature`の`kind: "string"`は**AST上の文字列リテラル値**(IPCチャンネル名など)を指しており、変数名・プロパティ名そのもの(識別子)は拾わない。ネイティブバイナリ解析用に文字列・プロシージャ名を横断検索できる`search`コマンドもあるが、これはディレクトリ(JS/Electronアプリ)には使えないことも、実際にエラーメッセージで確認した(`"This target is a directory..."`)。つまりJS解析では、未知の識別子を手がかりに横断検索する手段が今のところ無い。

## 「読みやすいソースの復元」は別の外部ツール前提だった

`recover-javascript-sources`(読みやすいJSモジュールを復元する機能)も試したが、こちらは失敗した。

```json
{
  "code": "capability_unavailable",
  "details": {
    "provider_id": "wakaru",
    "reason": "Provide an absolute REA_WAKARU_COMMAND pointing to Wakaru 1.13.0 on Linux x64; no tool is installed by REA"
  }
}
```

READMEのトップレベルの説明は「静的JS解析はHopper/Ghidra不要」と強調しているが、「読みやすいソースへの変換」は別の外部ツール(Wakaru)が必要で、これはREAが自動インストールしない。「Evidenceを取る」部分と「読みやすいソースに変換する」部分は別の依存関係を持つ、という点は実際に動かして初めて分かった。

## 追記: 2つの失敗は、両方とも実際に解決できた

記事公開前のレビューで、上記2つの失敗について「本当に解決できないのか」を実際に試してみた。結論から言うと、**どちらもREA自体の欠陥ではなく、ドキュメントに書かれていない運用上の前提**だった。

### 識別子の"no-match"は`node-id`シードで解決する

`trace_application_feature`の`seed.kind`には、ドキュメント化はされていないが`"node-id"`という選択肢もある(バリデーションエラーのメッセージから判明)。最初、Evidenceノードの`function_node_id`(`jsrg_node_*`という接頭辞)をそのままこれに渡してみたが、やはり`"no-match"`だった。これは別の内部グラフのIDだったためで、同じノードが持つ`application_node_ids`フィールドの方(`jag_node_*`という接頭辞)を渡すと、正しくマッチした。

```
seed: {"kind": "node-id", "value": "jag_node_df28...", "match": "exact"}
→ "coverage": {"status": "complete-within-source", "total_seed_matches": 1}
```

`coupon:debug`という文字列リテラルでトレースしたときと同じ28ノード・43エッジのグラフが、識別子`COUPON_DEBUG`を起点にしても再構築できた。つまり「識別子で検索したい」という要求自体は満たせるが、`analyze-javascript-application`の出力から該当ノードを自分で(またはエージェントが)検索し、正しい接頭辞のIDを取り出して渡す、という一手間が必要だった。

### Wakaruは普通にnpmで入り、単一ファイルを渡せば動く

エラーメッセージに書かれていた`wakaru@1.13.0`は、そのままnpmに公開されている(Apache-2.0)。

```bash
npm install wakaru@1.13.0
export REA_WAKARU_COMMAND="$(realpath node_modules/@wakaru/cli-linux-x64/wakaru)"
```

これで「Wakaru未導入」エラーは消えたが、代わりに「ディレクトリでなくファイルを渡せ」という別のエラーが出た。`recover-javascript-sources`は単一のバンドルファイル(webpackなどで1つにまとめられたminified JS)を入力に取る設計で、複数ファイル構成の`sample-app`ディレクトリをそのまま渡すのはそもそも対象外の使い方だった。対象を`sample-app/renderer/renderer.js`という単一ファイルに絞ると、`exit_code: 0`で正常終了し、復元済みモジュールが実際に出力された。

この修正はその後、誰でも再現できる形に落とし込んだ。`experiments/day-010/package.json`に`wakaru@1.13.0`をpinし、`npm install`だけで同じ環境が再現できるようにしてある。

## まとめ

- アプリの構造(IPC配線・公開API・ウィンドウ設定)の再構築は、数値レベルで完全に正確だった。
- 「隠しデバッグチャンネルが存在する」という事実自体は、最初の1回の解析で既にEvidenceの中に存在していた。
- しかし「なぜそれが隠し機能なのか(どの環境変数のどの値でゲートされているか)」という1文の説明は自動では出てこず、Evidenceグラフを自分で読んで繋ぐ必要があった。
- 今回のような軽度の難読化(短い変数名程度)であれば、人間が`lib/pricing.js`を直接読んでも10分かからず正解に到達できる。REAの価値は「その読む作業を省略してくれる」ことではなく、「正確な断片的事実(ファイル位置・confidence・コードフロー)を揃えて、読み間違いや見落としを減らしてくれる」ことにある、というのが実際に手を動かした上での結論。
- 最初に見つかった2つの失敗(識別子検索の"no-match"、Wakaru未導入によるソース復元失敗)は、どちらもREA自体の欠陥ではなく、ドキュメントに書かれていない運用上の前提が原因で、実際に両方とも解決できた。

検証に使ったコード・実行ログの全文は[本記事のGitHubリポジトリ](https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-010)に置いている。
