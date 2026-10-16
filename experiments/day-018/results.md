# Day 018 検証結果: morluto/rea (REA) で「ソース非公開」のminified JSを解析させる

## 検証対象・スコープ

today.md の指示に従い、**静的なJavaScript解析(Hopper/Ghidra/IDA等の商用解析ツールを使わない範囲)**
に限定して検証した。ネイティブバイナリ解析(Hopper/Ghidra/IDA連携)は今回のスコープ外。

- 検証対象ツール: [morluto/rea](https://github.com/morluto/rea) (npm: `rea-agents`, MIT license) v6.5.0
- 解析対象ソフトウェア: **jQuery 3.7.1 の `dist/jquery.min.js`**
  - 入手元: npm registry (`npm install jquery@3.7.1`)。jQuery自体は [MIT License](https://github.com/jquery/jquery/blob/main/LICENSE.txt)。
  - 公開されているビルド済みminifiedファイルを、先頭のライセンスコメント(`/*! jQuery v3.7.1 | ... */`、
    どのライブラリかが一目でわかってしまう)を取り除いた上で `bundle.js` という無名のファイル名に置き換え、
    「ソースコードも素性も非公開のアプリ」を模したテスト対象として使用した。
  - jQueryは十分に有名でソースが完全に公開されているため、REAが出した解析結果を**正解と直接比較できる**。
    これにより「REAの解析結果が実際に正しいか」を検証可能にした。
- 追加で使用した外部ツール: [wakaru](https://github.com/pionxzh/wakaru) v1.14.0 (npm: `wakaru`, **Apache-2.0**)。
  REAの `recover-javascript-sources` コマンドが内部で呼び出す外部デコンパイラ(詳細は後述)。

## 1. 導入ログ(`npx rea-agents setup`)

```
$ node --version
v22.22.0
$ npx -y rea-agents@latest --version
6.5.0
```

npmのpackage.jsonでは `"engines": {"node": ">=24.18.0 <25"}` と宣言されているが、
実際にはNode.js 22.22.0でも `--version` や各解析コマンドは問題なく動作した
(enginesはnpm installで警告される程度で、実行自体はブロックされない)。

`rea setup --dry-run --all-detected` を実行すると、このRoutineが動いているClaude Code自身を
"claude_code" クライアントとして検出し、以下のプランを提示した:

```
status: planned
plannedActions[2]:
  - id: "configure_client:claude_code"
    kind: configure_client
    label: Claude Code
    target: /root/.claude.json
    detail: "Add the REA MCP registration for Claude Code; preserve unrelated configuration.
             Command: npx -y rea-agents@6.5.0 mcp."
    backupPath: /root/.claude.json.rea.backup
  - id: "install_skill:claude_code"
    kind: install_skill
    label: REA skill for Claude Code
    target: /root/.claude/skills/reverse-engineer-anything
```

**実際にこの設定変更を適用することは見送った。** 理由: これはこのセッション自身が使っている
Claude Codeのグローバル設定ファイル(`/root/.claude.json`、リポジトリの外側)を書き換えるものであり、
変更を反映するには「クライアントの再起動」が必要になる。自動実行のRoutineは自分自身を再起動できず、
再起動を伴わない場合は登録しても検証中に有効にならない。これは「ツールの既定動作の問題」ではなく、
無人実行のRoutine環境固有の制約(CLAUDE.mdの「Routine環境の制約」に該当)と判断した。

代わりに、REAが `--help` で示す通りMCPツールと同じコマンド群はCLIサブコマンドとしても
直接実行できる(`Integrations: mcp  Register as MCP server (add, doctor)` とある通り、
`mcp` はCLIの一機能として追加されているだけで、153個のCLIコマンドと207個のMCPツールは
同じ実装を呼ぶ)。そのため、本検証では **MCP経由ではなくCLIサブコマンドを直接実行**して
REAの解析エンジンそのものを検証した。これはツールの代替呼び出し経路であり、検証結果の正しさには
影響しない。

`rea doctor` の結果:

```
healthy: false
environment_healthy: false
scope_checks:
  - node: ok (22.22.0)
  - host: ok (ubuntu 24.04)
  - hopper: missing_analysis_engine (スコープ外、意図的に未導入)
  - ghidra: missing_analysis_engine (スコープ外、意図的に未導入)
  - ida-registration: missing_analysis_engine (スコープ外、意図的に未導入)
  - jadx: missing_analysis_engine (スコープ外、意図的に未導入)
  - skill:identity: config_drift (MCP未登録のため)
  - registration:claude_code: config_drift (MCP未登録のため)
identity.catalog.counts:
  cli_commands: 153
  mcp_tools: 207
  mcp_prompts: 6
```

`healthy: false` はHopper/Ghidra/IDA/jadxが入っていないことと、MCP未登録によるもので、
いずれも今回のスコープ外範囲・意図した選択によるもの。Node.js/ホスト自体は正常。

## 2. 静的解析: `analyze-javascript-application`

```
$ npx rea-agents@latest analyze-javascript-application ./blind-target --format json
```

`blind-target/` には `bundle.js`(素性を隠したjQuery minified, 87,444 bytes)と
最低限の `package.json`(`{"name":"mystery-app","version":"1.0.0"}`)だけを置いた。

実行は完全にローカルで完結し(外部への通信は発生しない)、終了コード0で成功した。

結果(`normalized_result.statistics`):

```json
{
  "relevant_files": 2,
  "parsed_javascript_files": 1,
  "visited_ast_nodes": 30926,
  "findings": 1,
  "parse_failures": 0
}
```

**面白かった点:** 87KBの入力ファイル1つに対し、生成された `semantic_graph` (AST上のあらゆる
意味的関係を記録したEvidence JSON)は **約40MB(40,644,013文字)** にもなった。
出力全体(`--format json`)は38,459,421バイト。入力サイズの約440倍に膨張する。
これはREAの設計が「人間が結果を直接読む」のではなく「エージェントが `--token-limit` や
`inspect-analysis-view` 等で必要な部分だけを継続的に問い合わせる」ことを前提にしているためと考えられる
(実際、巨大なEvidence JSONを素のまま人間やLLMのコンテキストに渡すのは非現実的)。

`normalized_result.summary` ではElectron固有の項目(`browser_windows`, `ipc.*`,
`native_addon_bindings` 等)がすべて0と判定されており、jQueryが素のUMDライブラリで
Electronアプリではないことを正しく認識できていた。

グラフのノード数は6個で、入力が単一ファイルのUMDビルドであるため
`javascript-module` ノードは実質1つ(`bundle.js` 全体)にしかならなかった。
webpack等で複数モジュールに分割されたバンドルであれば、モジュール境界ごとに
もっと多くのノードができると推測されるが、今回の対象では検証できていない(スコープ外)。

生成された巨大な `semantic_graph` 全体はリポジトリに含めず、要約を
`samples/analyze-javascript-application-summary.json` として保存した。

## 3. コード復元: `recover-javascript-sources`

### 3-1. 最初の試行: Wakaruが別途必要

```
$ npx rea-agents@latest recover-javascript-sources \
    /abs/path/blind-target/bundle.js /abs/path/recovered
```

これは**失敗した**(ツール自体の仕様に関わる失敗、記事に書く対象):

```json
{
  "code": "capability_unavailable",
  "category": "unsupported_provider",
  "message": "Provide an absolute REA_WAKARU_COMMAND pointing to a Wakaru ^1.13.0 Linux x64 binary
               (verified with 1.14.0); no tool is installed by REA. See docs/javascript-recovery.md#install-wakaru.",
  "details": {"provider_id": "wakaru", "operation": "recover_javascript_sources"}
}
```

REAの `recover-javascript-sources` は単体では動作せず、**別途 [wakaru](https://github.com/pionxzh/wakaru)
(Apache-2.0のJavaScriptデコンパイラ、Rust製)を自分で用意して `REA_WAKARU_COMMAND` 環境変数で
バイナリのパスを渡す必要がある。** READMEや `--help` の文面だけでは気づきにくく、
実際に実行してエラーメッセージを読むまでこの依存に気づかなかった。

Wakaruはnpmで配布されており(`npm install wakaru@1.14.0`)、ライセンス上・導入手順上も
追加の有料APIキーやGPUは不要だったため、今回のスコープ内で導入できた:

```
$ npm install wakaru@1.14.0 --no-save
$ node_modules/@wakaru/cli-linux-x64/wakaru --version
wakaru 1.14.0
```

### 3-2. Wakaru導入後の再試行: 成功

```
$ export REA_WAKARU_COMMAND=/abs/path/node_modules/@wakaru/cli-linux-x64/wakaru
$ npx rea-agents@latest recover-javascript-sources \
    /abs/path/blind-target/bundle.js /abs/path/recovered --format json
```

終了コード0で成功。出力:

```json
{
  "report": {"detected_formats": ["amd"], "safety": "normal",
             "modules": [{"filename": "module.js", "status": "decompiled"}],
             "total": 1, "failed": 0, "elapsed_ms": 549},
  "normalized_result": {
    "runtime_equivalence": "unknown",
    "limitations": [
      "Recovered sources are derived artifacts; original variable names and runtime equivalence are not established.",
      "..."
    ]
  }
}
```

87,444バイトのminifiedな入力から、191,015バイト・6,341行の読みやすい `module.js` が
0.549秒(Wakaruの処理時間)で生成された。REA/Wakaru自身も `runtime_equivalence: "unknown"`
(実行時の等価性は保証しない)と明記しており、過大な信頼はしていない誠実な出力だった。

`detected_formats: ["amd"]` という判定は少し意外だった。jQueryのビルドはCommonJS/AMD/グローバルの
どれでも動くUMDラッパーだが、Wakaruの構造的バンドル検出はこれを(厳密にはUMDだが)AMD系として
分類したようだ。単一ファイルのライブラリであり、webpack的な複数モジュールバンドルではないため、
`--unpack=strict` の構造検出としては妥当な判定と考えられる。

### 3-3. 復元結果の正しさを実際のjQueryソースと比較検証

`recover-javascript-sources` が生成した `module.js` から、jQueryの型判定ユーティリティ
`toType()` に対応する関数を見つけて、実際のjQuery 3.7.1ソース(`dist/jquery.js`、非minified)
と比較した。

**実際のjQueryソース(`dist/jquery.js` 134-142行目):**

```js
function toType( obj ) {
	if ( obj == null ) {
		return obj + "";
	}

	return typeof obj === "object" || typeof obj === "function" ?
		class2type[ toString.call( obj ) ] || "object" :
		typeof obj;
}
```

**REA + Wakaruが復元したコード(`samples/recovered-module.js`、変数名は自動付与):**

```js
function x(e) {
    if (e == null) {
        return `${e}`;
    }
    if (typeof e === "object" || typeof e === "function") {
        return n[toString.call(e)] || "object";
    }
    return typeof e;
}
```

変数名(`obj`→`e`, `class2type`→`n`)や三項演算子からif文への書き換えはあるが、
**ロジックは完全に一致している。** 「素性を隠したminified JSから、元の関数の挙動を
正しく復元できる」という、REAが主張する能力を具体的なコードレベルで確認できた。

### 3-4. 見つかったバグ: 正規表現リテラル中の `\0` エスケープがNULバイトに壊れる

`node --check samples/recovered-module.js` は構文エラーなく通ったが、
`grep` でファイル内を検索すると `grep: ...: binary file matches` と表示され、
テキストファイルとして扱われないことに気づいた。調べたところ、
**復元結果の343行目に実際のNUL(0x00)バイトがそのまま埋め込まれていた。**

元のjQueryソース(`dist/jquery.js` 673-674行目、CSS識別子にマッチする正規表現の一部):

```js
identifier = "(?:\\\\[\\da-fA-F]{1,6}" + whitespace +
	"?|\\\\[^\\r\\n\\f]|[\\w-]|[^\0-\\x7f])+",
```

ここでの `\0` はソースコード上は2文字(バックスラッシュと`0`)で、実行時にNUL文字相当の
エスケープとして評価される、何も特殊ではない通常のJS文字列リテラルの書き方。

復元結果(`samples/recovered-module.js` 343行目、`cat -v` でNULを`^@`として可視化):

```
const t = `(?:\\[\da-fA-F]{1,6}${ge}?|\\[^\r\n\f]|[\w-]|[^^@-\x7f])+`;
```

`\0` の部分が、エスケープ済みの2文字のテキストとしてではなく、**実際の生のNULバイトとして
ファイルに書き込まれてしまっている**(同じ行の `\x7f` の方は正しく2文字のエスケープ文字列の
まま保持されている)。文字列の実行時の値としては結果的に等価(どちらもNUL文字1個を表す)なため
`node --check` は通り、構文的には壊れていないが、`recover-javascript-sources` という
「読みやすいソースを復元する」ことを目的としたコマンドの出力に、エディタや `grep` ・`git diff`
から見ると不可視・不可解な制御文字が混入するのは、ツールの目的(可読性の復元)に対しては
明確な不具合だと言える。文字列の連結(`"a" + "b"`)をテンプレートリテラル(`` `a${x}b` ``)に
書き換えるWakaruの変換パスで、エスケープシーケンスの再エスケープ処理に一貫性がない
(`\x7f` は正しく処理されるが `\0` は評価後の生バイトになる)ことが原因と推測される。

## 4. 結論・まとめ

- REAはminified/素性非公開のJavaScript(今回: jQuery 3.7.1のビルド済みファイル)に対して、
  静的解析(`analyze-javascript-application`)とソース復元(`recover-javascript-sources`、
  Wakaru経由)の両方を**追加の有料APIキー・GPUなしで実行できた。**
- 復元されたコードは、少なくとも検証した1関数(`toType`)についてはロジックが完全に正しく、
  「ソース非公開のアプリの挙動を復元する」という主張に説得力があった。
- 一方で、`recover-javascript-sources` はREA単体では動作せず外部ツール(Wakaru)が別途必要
  という、ドキュメントだけでは気づきにくい依存があった。また、復元結果の一部に
  エスケープ文字がNULバイトに壊れるという具体的な不具合を見つけた。
- MCP経由での呼び出し(Claude Codeへの本登録)は、実行環境(無人のRoutine)の制約により
  見送り、同じ処理を呼ぶCLIサブコマンドで代替検証した。
- ネイティブバイナリ解析(Hopper/Ghidra/IDA連携)は今回のスコープ外。
