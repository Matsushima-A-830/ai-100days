---
title: "ソース非公開のJSをAIエージェントに解析させるREA、実際にどこまで正しいか検証した"
emoji: "🔍"
type: "tech"
topics: ["ai", "llm", "javascript", "mcp", "reverseengineering"]
published: false
---

## これは何か

coding agent(Claude Code等)にネイティブバイナリやJavaScript/Electronアプリを解析させ、「ソースコードは復元しないが機能の挙動を調査する」ことを目的としたMCPサーバー/CLIツール[REA(morluto/rea)](https://github.com/morluto/rea)(MITライセンス)を、実際に手を動かして検証した。

今回は検証範囲を**静的なJavaScript解析(Hopper/Ghidra/IDA等の商用解析ツールを使わない範囲)**に絞った。ネイティブバイナリ解析はスコープ外。

検証対象ソフトウェアには、[jQuery 3.7.1](https://github.com/jquery/jquery)のビルド済みminifiedファイル(`dist/jquery.min.js`、MIT License)を使った。npm registryから取得できる公開済みの配布物であり、再配布・解析に問題はない。jQueryは「素性も実装もよく知られている」ソフトウェアなので、REAが出した解析結果を**実際のソースコードと直接比較して正しさを検証できる**という利点がある。

先頭のライセンスコメント(`/*! jQuery v3.7.1 | ... */`。これだけで何のライブラリかわかってしまう)を取り除き、ファイル名も `bundle.js` という無名のものに変えて、「ソースコードも素性も非公開のアプリ」を模した。

出典:
- REA: https://github.com/morluto/rea (MIT)
- jQuery: https://github.com/jquery/jquery (MIT)
- Wakaru: https://github.com/pionxzh/wakaru (Apache-2.0、後述)

## 導入

Node.js 22.22.0で検証した(npmのpackage.jsonは`node >=24.18.0 <25`を要求しているが、実際には22系でも動作した)。

```
$ npx -y rea-agents@latest --version
6.5.0
```

`rea doctor` でヘルスチェックすると、Node.js/ホストは正常、Hopper/Ghidra/IDA/jadxは(今回意図的に導入していないため)`missing_analysis_engine` と出る。これらはスコープ外として扱っているので問題ない。

```
identity.catalog.counts:
  cli_commands: 153
  mcp_tools: 207
  mcp_prompts: 6
```

REAは153個のCLIコマンドと207個のMCPツールを持つ。`--help`を見ると `mcp` はこのCLIの一機能として実装されており、MCPツールとCLIサブコマンドは同じ解析エンジンを呼んでいる。

**今回はMCP経由ではなくCLIサブコマンドを直接実行して検証した。** `rea setup` は検証に使っているClaude Code自身のグローバル設定ファイル(リポジトリの外)を書き換え、反映にはクライアントの再起動が必要になるため、無人実行の検証プロセスではMCP登録そのものは見送った。同じ解析エンジンをCLIから直接叩けば結果は変わらないため、検証の正しさには影響しない。

## 静的解析: `analyze-javascript-application`

```
$ npx rea-agents@latest analyze-javascript-application ./blind-target --format json
```

87,444バイトの匿名化したjQuery minifiedファイル1つに対して実行すると、外部への通信なしに完全ローカルで解析が完了した(終了コード0)。

```json
{
  "relevant_files": 2,
  "parsed_javascript_files": 1,
  "visited_ast_nodes": 30926,
  "findings": 1,
  "parse_failures": 0
}
```

面白かったのは出力サイズで、この87KBの入力に対して生成された解析結果(Evidence JSON、AST上のあらゆる意味的関係を記録したグラフ)は**約38MB**にもなった。入力の約440倍である。これは「人間が直接結果を読む」のではなく「エージェントが必要な部分だけを`--token-limit`等で少しずつ問い合わせる」設計を前提にしているためだと考えられる。

また `summary` ではElectron固有の項目(`browser_windows`、IPC関連、ネイティブアドオン等)がすべて0と判定されており、jQueryが素のライブラリでElectronアプリではないことを正しく認識していた。

## コード復元: `recover-javascript-sources`、まず失敗

```
$ npx rea-agents@latest recover-javascript-sources ./blind-target/bundle.js ./recovered
```

```json
{
  "code": "capability_unavailable",
  "message": "Provide an absolute REA_WAKARU_COMMAND pointing to a Wakaru ^1.13.0 Linux x64 binary (verified with 1.14.0); no tool is installed by REA."
}
```

REAの「コード復元」機能は単体では動かず、別途[Wakaru](https://github.com/pionxzh/wakaru)(Apache-2.0、Rust製のJavaScriptデコンパイラ)を自分で用意し、環境変数`REA_WAKARU_COMMAND`でバイナリの絶対パスを渡す必要がある。`--help`だけでは気づきにくく、実際に実行してエラーメッセージを読むまでわからなかった。

幸いWakaruはnpmで配布されているため(`npm install wakaru@1.14.0`)、追加の有料APIキーなしですぐに導入できた。

```
$ npm install wakaru@1.14.0 --no-save
$ node_modules/@wakaru/cli-linux-x64/wakaru --version
wakaru 1.14.0
```

## コード復元、再挑戦: 成功

```
$ export REA_WAKARU_COMMAND=/abs/path/node_modules/@wakaru/cli-linux-x64/wakaru
$ npx rea-agents@latest recover-javascript-sources \
    ./blind-target/bundle.js ./recovered --format json
```

```json
{
  "report": {"detected_formats": ["amd"], "modules": [{"status": "decompiled"}],
             "total": 1, "failed": 0, "elapsed_ms": 549},
  "runtime_equivalence": "unknown"
}
```

今度は成功した。87,444バイトのminifiedな入力から、191,015バイト・6,341行の読みやすいJavaScriptファイルが0.549秒で生成された。`runtime_equivalence: "unknown"`(実行時の等価性は保証しない)と出力自身が明記している点は、過大な宣伝をしない誠実な設計だと感じた。

### 復元結果は実際に正しいのか

jQueryの型判定ユーティリティ`toType()`に対応する関数で、実際のソースと比較した。

実際のjQuery 3.7.1ソース(`dist/jquery.js`):

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

REA + Wakaruが復元したコード:

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

変数名(`obj`→`e`)や制御構造(三項演算子→if文)は変わっているが、**ロジックは完全に一致している。**「ソース非公開のコードから元の挙動を復元する」という主張を、具体的な関数レベルで確認できた。

### 見つかった不具合: `\0` エスケープがNULバイトに壊れる

復元結果を`node --check`すると構文エラーはなかったが、`grep`で検索すると`grep: ...: binary file matches` と表示され、テキストファイルとして扱われないことに気づいた。

原因は、復元結果343行目の正規表現リテラル中に**実際のNUL(0x00)バイトがそのまま埋め込まれていた**ことだった。

元のソース(CSS識別子にマッチする正規表現の一部):

```js
"?|\\\\[^\\r\\n\\f]|[\\w-]|[^\0-\\x7f])+",
```

ここでの`\0`は普通のJS文字列エスケープ(2文字のテキスト)だが、復元結果ではこの部分だけが生のNULバイトとして出力されていた(同じ行の`\x7f`は正しく2文字のまま保持されている)。文字列の実行時の値としては結果的に等価なので構文は壊れないが、「読みやすいソースを復元する」というツールの目的からすれば、エディタや`grep`・`git diff`で不可解な制御文字として見えてしまうのは明確な不具合だ。文字列連結をテンプレートリテラルに書き換える変換パスで、エスケープシーケンスの再エスケープ処理に一貫性がないことが原因と推測される。

## まとめ

- REAはminified/素性非公開のJavaScriptに対して、静的解析とコード復元の両方を**追加の有料APIキー・GPUなしで実行できた。**
- 検証した1関数については復元結果のロジックが実際のソースと完全に一致しており、「ソース非公開のアプリの挙動を復元する」という主張には具体的な説得力があった。
- 一方で、コード復元機能は単体では動作せず外部ツール(Wakaru)が別途必要というドキュメントだけでは気づきにくい依存があり、復元結果にはエスケープ文字がNULバイトに壊れるという具体的な不具合も見つかった。

リバースエンジニアリング系のツールであるため、検証対象は自分で用意したMITライセンスの公開配布物(jQuery)に限定し、教育・検証目的での利用である。
