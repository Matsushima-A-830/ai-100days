---
title: "grepの代わりに1クエリでコードを返す「codegraph」をalias解決と重複コードで検証した"
emoji: "🕸️"
type: "tech"
topics: ["ai", "mcp", "typescript", "codeanalysis", "llm"]
published: false
---

## 概要

[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)(MIT License)は、コーディングエージェント(Claude Code・Cursor・Codex CLIなど)向けに、ローカルのSQLiteに関数・クラスなどのシンボルと呼び出し/参照関係を事前インデックスし、MCP経由またはCLIで公開するツールである。本日時点でGitHub TrendingのTypeScript部門で+99star/日を記録していた。

「エージェントがgrep/Readを何度も繰り返す代わりに、1回のクエリで関連コードを取得できる」という主張を、自分のリポジトリ(本チャレンジのai-100daysリポジトリ自身、159ファイル・Python/JavaScript/C#/Rust混在)に対して実際に手を動かして検証した。
ローカルPC(WSL2、Node.js v26.8.2)でも同じ手順を実行し、ファイルが163に増えた状態(2.1秒でインデックス完了)で、以下のクエリ結果がすべて同じになることを確認した。

日本語記事はZenn 0件・note 0件だったが、Qiita記事が1件見つかった(自社リポジトリで試した実利用レポート)。この記事は「同じ判定を独立に再実装した重複コードは、対象4箇所中2箇所しか検出できなかった」と報告している。この限界が自分の環境でも再現するかどうかも含めて検証した。

## 導入とインデックス構築

```
$ time (npx -y @colbymchenry/codegraph init .)
T  Initializing CodeGraph
Scanning files...
Parsing code...
Resolving refs...
Linking dynamic dispatch...
*  Indexed 159 files
•  2,162 nodes, 4,700 edges in 2.6s
—  Done

real    0m3.676s
```

追加のAPIキーもGPUも不要で、`npx`一発で導入できた。
リポジトリルートに `.codegraph/codegraph.db`(SQLite、約7.3MB)が生成され、自動で`.gitignore`も作られる。

初回実行時には、次の1行が表示された。

```
codegraph collects anonymous usage stats (no code, paths, or names) — "codegraph telemetry off" or CODEGRAPH_TELEMETRY=0 disables.
```

匿名の利用統計の送信は既定で有効(オプトアウト方式)である。
`~/.codegraph/telemetry-queue.jsonl`に溜まった送信待ちのデータを見ると、`init`と`version`を実行した時点では`{"k":"cli_command","n":"init","c":1,...}`のようにコマンド名と回数だけだった。
`codegraph telemetry off`で止めると、未送信のデータも削除される。
業務のリポジトリで使う場合は、最初に`CODEGRAPH_TELEMETRY=0`を設定しておくとよい。

`codegraph status`で内訳も見える。

```
Files:     159
Nodes:     2,162
Edges:     4,700
DB Size:   7.33 MB

Nodes by Kind:
  function        549
  variable        513
  import          477
  method          209
  file            156
  constant        102
  class           75
```

## 単純な呼び出し関係は正確だった

`tools/video/render.py`の`render_frame`関数を対象に`callers`/`callees`を試した。

```
$ npx -y @colbymchenry/codegraph callers render_frame
Callers of "render_frame" (1):
function    main
  tools/video/render.py:525, 549

$ npx -y @colbymchenry/codegraph callees render_frame
Callees of "render_frame" (5):
function    chrome               tools/video/render.py:294
function    scene_architecture   tools/video/render.py:369
function    caption              tools/video/render.py:310
variable    FADE [references]    tools/video/render.py:40
variable    SCENES [references]  tools/video/render.py:453
```

実際のソースを`grep -n "^def " tools/video/render.py`で確認すると、`main()`は491行目から始まる関数で、525行目・549行目は確かにその内部からの呼び出しだった(`render_frame`自身の再帰呼び出しではない)。この単純なケースでは呼び出しグラフの結果は正確だった。

## クロスファイルのexport alias解決は本物だった

もう少し難しいケースも試した。
`experiments/day-010/sample-app/lib/pricing.js`には内部関数`_q`があり、`module.exports = { quote: _q, ... }`という形で`quote`という別名でエクスポートされている。呼び出し側の`main.js`は`const { quote } = require('./lib/pricing')`で destructuring import している。

```
$ npx -y @colbymchenry/codegraph callers _q
Callers of "_q" (2):
function _q (javascript) — experiments/day-010/sample-app/lib/pricing.js:9
file        main.js
  experiments/day-010/sample-app/main.js:22
file        pricing.js [references]
  experiments/day-010/sample-app/lib/pricing.js:30
```

`main.js:22`の実際のコードは

```js
return quote(String(code || ''), Number(subtotal) || 0);
```

で、ソース上には`_q`という文字列はどこにも現れない。それでもcodegraphは「`_q`の実体 → `quote`としてのエクスポート → `main.js`での呼び出し」という連鎖を正しく解決し、callerとして`main.js:22`を返した。単純な文字列検索(`grep "_q("`)では見つからないケースであり、これはgrep/Readの繰り返しよりも優れている具体的な例だと言える。

一方で、**逆方向の検索はできなかった**。

```
$ npx -y @colbymchenry/codegraph callers quote
[i] Symbol "quote" not found — did you mean: cols, urllib.parse?
```

シンボル検索の`query quote`も試したが、`quote_volume`という文字列を含む配列や`from urllib.parse import quote`のような無関係なものが返るだけで、`_q`には辿り着かなかった。

呼び出し側で実際に目にする名前`quote`で検索しても見つからない。インデックスは元の宣言名(`_q`)でしか引けないため、「呼び出し元のコードを読んで知った名前」で検索すると`Symbol not found`になる。grepを完全に代替するには、結局ソースを一度読んで本当の名前を知る必要がある場面が残っている。

## Qiita記事が報告した「重複コード検出不可」の再現

Qiita記事が報告していた限界を、独立した最小ケースで再現した。ロジックが同一だが、明らかに別の人(別の意図)が書いたことを想定した2つの関数を用意した。

```python
# experiments/day-060/duplicate-test/a.py
def validate_email_signup(email: str) -> bool:
    if "@" not in email:
        return False
    local, _, domain = email.partition("@")
    return bool(local) and "." in domain
```

```python
# experiments/day-060/duplicate-test/b.py
def check_email_format(address: str) -> bool:
    if "@" not in address:
        return False
    local, _, domain = address.partition("@")
    return bool(local) and "." in domain
```

`codegraph sync`でインデックスを更新した後、`validate_email_signup`の影響範囲を調べる。

```
$ npx -y @colbymchenry/codegraph impact validate_email_signup
Impact of changing "validate_email_signup" — 1 affected symbols:
function validate_email_signup (python) — experiments/day-060/duplicate-test/a.py:1

$ npx -y @colbymchenry/codegraph callers validate_email_signup
Callers of "validate_email_signup" (0):
[i] No callers found for "validate_email_signup"
```

`check_email_format`との関連は一切示されなかった。呼び出し関係・参照関係がグラフ上に存在しない限り、ロジックが完全に同一でも無関係なシンボルとして扱われる。

さらに、自然言語クエリを受け付ける`context`コマンドでも試した。

```
$ npx -y @colbymchenry/codegraph context "refactor email validation logic to share one implementation"
```

結果は`validate_email_signup`をEntry Pointとして拾ったが、`check_email_format`には一切触れず、代わりに全く無関係な`experiments/day-035`(Unityのゲーム実験)の`OnEnable`メソッドなどを返した。出力の末尾には次の警告が付いていた。

```
⚠️ Low-confidence match
This query matched mostly on common words, so the entry points above may be off-target
```

ツールが自分の検索の信頼度の低さを正直に警告する設計である点は評価できる。裏を返せば、重複コードを探すという用途には`context`/`explore`の自然言語検索もグラフ検索も効かないということでもある。Qiita記事の報告(4箇所中2箇所しか検出できなかった)と一致する挙動であり、ツールのバグではなく、「呼び出し/参照グラフ」という設計そのものに由来する本質的な限界だと判断できる。

## 追加で見つかった限界: 汎用的なシンボル名

`main`のような汎用的な関数名を`explore`に渡すと、`tools/video/render.py`とは一切関係ない`experiments/day-021/mcp_client_build_room.py`や`experiments/day-025/akv_generate_check.py`などの`main`関数まで一緒に返ってきた。シンボル名が同じであれば、ファイルの文脈に関わらず全件が候補として扱われており、名前の衝突を意味的に区別する機能は無いようだった。

## grep/Readの繰り返し vs 1回のクエリ

| ケース | grep/Read | codegraph |
|---|---|---|
| 同一ファイル内の呼び出し元 | `grep -n "render_frame(" file.py` で十分(1コマンド) | `codegraph callers render_frame`(1コマンド、同程度) |
| exportのalias経由のクロスファイル呼び出し元 | `grep`では`_q`で検索してもヒットしない。`main.js`の`require`文を人間が読んで追う必要がある(複数ファイルをRead) | `codegraph callers _q`で1コマンド解決。ただし呼び出し側の名前(`quote`)では検索不可 |
| 重複コード(呼び出し関係なし) | 目で見比べるしかない | 検出できない(grepと同程度か、むしろ「無関係」と断定されるため気づきにくい) |

同一ファイル内の単純な検索では大差ないが、**exportのalias解決を伴うクロスファイルの追跡では、複数ファイルの手動Readを1回のクエリで省略できた。** 一方、重複コードの発見や「呼び出し側で見た名前からの逆引き」は、grepも苦手だがcodegraphも解決していない。

## まとめ

- 導入・インデックス構築はAPIキー・GPU不要で高速(159ファイル・2.6秒、ローカルPCでは163ファイル・2.1秒)という触れ込みは正確だった。ただし匿名の利用統計の送信が既定で有効なので、`CODEGRAPH_TELEMETRY=0`で止めてから使う。
- 単純な同一ファイル内の呼び出し関係は正確だった。
- クロスファイルのexport alias解決は、grepでは追いにくいケースで明確に優位性を確認できた。
- 一方、宣言時の元の名前でしか検索できない(呼び出し側で見た名前では見つからない)という制約も確認した。
- Qiita記事が報告した「独立に再実装された重複コードを検出できない」という限界は、自作の最小ケースで再現を確認した。これはグラフベースの設計に由来する本質的な限界であり、「grepの代わりに1クエリ」という主張はコールグラフが追える範囲に限定して理解すべきだとわかった。

## 出典・ライセンス

- https://github.com/colbymchenry/codegraph (MIT License)
- npm: https://www.npmjs.com/package/@colbymchenry/codegraph (検証バージョン: 1.6.4)
- テレメトリの説明: https://github.com/colbymchenry/codegraph/blob/main/TELEMETRY.md
