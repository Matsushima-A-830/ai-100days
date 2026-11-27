# Day 060 検証結果: colbymchenry/codegraph

- 出典: https://github.com/colbymchenry/codegraph (MIT License)
- バージョン: 1.6.4 (`npx -y @colbymchenry/codegraph version`)
- 検証対象: 本リポジトリ (ai-100days) 自身
- 検証環境: Routineクラウド実行環境(GPUなし、ネットワーク制限あり。ただしnpm registryへの到達は可能だった)

## 1. 導入とインデックス構築

```
$ time (npx -y @colbymchenry/codegraph init . )
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

追加のAPIキー・GPUは不要。`npx` 経由で即座にインストールでき、リポジトリルートに `.codegraph/codegraph.db` (SQLite, 約7.3MB) が作られる。`.gitignore` も自動生成されたため、本リポジトリの `.gitignore` にも `.codegraph/` を追記した。

`codegraph status` の出力(抜粋):

```
Files:     159
Nodes:     2,162
Edges:     4,700
DB Size:   7.33 MB
Backend:   node:sqlite - built-in (full WAL)

Nodes by Kind:
  function        549
  variable        513
  import          477
  method          209
  ...

Files by Language:
  python          97
  javascript      40  (36 with symbols)
  csharp          15
  yaml            3
  c               2
  rust            2
```

完全ログ: `init-log.txt`, `status-log.txt`

## 2. クエリ・呼び出しグラフの正確性(検証できた範囲)

`tools/video/render.py` の `render_frame` 関数を対象に `callers` / `callees` を実行し、実際のソースコードと目視で照合した。

```
$ npx -y @colbymchenry/codegraph callers render_frame
Callers of "render_frame" (1):
function    main
  tools/video/render.py:525, 549

$ npx -y @colbymchenry/codegraph callees render_frame
Callees of "render_frame" (5):
function    chrome       tools/video/render.py:294
function    scene_architecture  tools/video/render.py:369
function    caption      tools/video/render.py:310
variable    FADE [references]  tools/video/render.py:40
variable    SCENES [references] tools/video/render.py:453
```

`grep -n "^def " tools/video/render.py` で確認した結果、`main()` は456行目の `render_frame` 定義より後の491行目から始まる関数で、525行目・549行目は確かに `main()` 内部の呼び出しだった(`render_frame` 自身の再帰呼び出しではない)。**この単純なケースでは呼び出しグラフは正確だった。**

### クロスファイル・alias解決の確認(重要な発見)

`experiments/day-010/sample-app/lib/pricing.js` は内部関数 `_q` を `module.exports = { quote: _q, ... }` で `quote` という別名でエクスポートしている。呼び出し側の `main.js` は `const { quote } = require('./lib/pricing')` で destructuring import している。

```
$ npx -y @colbymchenry/codegraph callers _q
Callers of "_q" (2):
function _q (javascript) — experiments/day-010/sample-app/lib/pricing.js:9
file        main.js
  experiments/day-010/sample-app/main.js:22
file        pricing.js [references]
  experiments/day-010/sample-app/lib/pricing.js:30
```

`main.js:22` の実際のコードは `return quote(String(code || ''), Number(subtotal) || 0);` で、ソースコード上には `_q` という文字列は一切現れない。それでも codegraph は `_q`(実体)→`quote`(エクスポート時のalias)→呼び出し元という連鎖を正しく解決し、`main.js:22` を callerとして返した。**単純なgrepでは `_q` という文字列で検索しても見つからないため、これはgrep/Readの繰り返しより優れている具体例。**

一方で、**逆方向には解決できなかった**:

```
$ npx -y @colbymchenry/codegraph callers quote
[i] Symbol "quote" not found — did you mean: cols, urllib.parse?
```

呼び出し側で実際に使われている名前 `quote` でシンボル検索しても見つからない。インデックスは元の宣言名 `_q` でしか引けないため、「呼び出し元のコードを読んで知った名前」で検索しても `Symbol not found` になる。grepを完全に代替するには、結局ソースを読んで本当の名前を知る必要がある場面が残る。

## 3. Qiita記事が報告する限界の再現(重複コード検出)

Qiita記事(日本語記事検索時点で1件ヒット)が報告していた「独立に再実装された重複コードは呼び出し関係が無いため検出できない」という限界を、自前の最小ケースで再現した。

`experiments/day-060/duplicate-test/a.py`:
```python
def validate_email_signup(email: str) -> bool:
    if "@" not in email:
        return False
    local, _, domain = email.partition("@")
    return bool(local) and "." in domain
```

`experiments/day-060/duplicate-test/b.py`(ロジックは同一だが独立に書いた体):
```python
def check_email_format(address: str) -> bool:
    if "@" not in address:
        return False
    local, _, domain = address.partition("@")
    return bool(local) and "." in domain
```

`codegraph sync` 後、`validate_email_signup` の `impact` / `callers` を実行:

```
$ npx -y @colbymchenry/codegraph impact validate_email_signup
Impact of changing "validate_email_signup" — 1 affected symbols:
function validate_email_signup (python) — experiments/day-060/duplicate-test/a.py:1

$ npx -y @colbymchenry/codegraph callers validate_email_signup
Callers of "validate_email_signup" (0):
[i] No callers found for "validate_email_signup"
```

**`check_email_format` との関連は一切示されなかった。** 呼び出し関係・参照関係がグラフ上に存在しない限り、ロジックが完全に同一でも無関係なシンボルとして扱われることを確認した。Qiita記事の報告(4箇所中2箇所しか検出できなかった)と一致する挙動であり、これはツールの設計(呼び出し/参照グラフであり、意味的類似度の検索ではない)に由来する本質的な限界と判断できる。

さらに、自然言語クエリの `context` コマンドでも同じ限界を確認した:

```
$ npx -y @colbymchenry/codegraph context "refactor email validation logic to share one implementation"
```

結果は `validate_email_signup` をEntry Pointとして拾ったものの、`check_email_format` には触れず、代わりに全く無関係な `experiments/day-035/signal-lost-game` (Unity/C#) の `OnEnable` メソッドなどを返した。出力自体が `⚠️ Low-confidence match` と自己申告しており、"may be off-target" と明記していた。ツール自身が低信頼度を検知して正直に警告する設計である点は評価できるが、裏を返せば「重複コードを探す」という用途には `context`/`explore` の自然言語検索もグラフ検索も効かないことを意味する。

完全ログ: `duplicate-test-result.txt`

## 4. 追加の限界: 汎用的なシンボル名での `explore`

`main` のような汎用的な関数名を指定すると、リポジトリ全体に散らばる無関係な `main` 関数(`experiments/day-021/mcp_client_build_room.py`, `experiments/day-025/akv_generate_check.py` など、`tools/video/render.py` とは一切関係ないファイル)が一緒に返ってくることを確認した(`explore-render.txt`)。シンボル名の衝突を意味的に区別する機能はなく、名前が同じであれば全件が候補として扱われる。

## 5. grep/Readの繰り返し vs 1回のクエリ(比較)

| ケース | grep/Readでの手順 | codegraphでの手順 |
|---|---|---|
| 同一ファイル内の呼び出し元を知りたい(`render_frame`) | `grep -n "render_frame(" tools/video/render.py` → 3行をすぐ特定できた(1コマンド) | `codegraph callers render_frame`(1コマンド、定義場所や行番号の解釈も不要) |
| alias経由のクロスファイル呼び出し元を知りたい(`_q`→`quote`) | `grep -rn "_q(" .` ではヒットしない(exportsのaliasを追う必要があり、`main.js`を手動で開いて`require`の行を読む必要がある。最低2ファイルをRead) | `codegraph callers _q`(1コマンドで解決。ただし呼び出し側の名前`quote`では検索できず、結局元の宣言名を知る必要がある) |
| 重複コード(呼び出し関係なし)を見つけたい | 文字列的な類似度・ロジックを比較しながら目で見るしかない(今回のケースでは2ファイルを読めば一致に気づける規模) | `impact`/`callers`/`context` いずれも無関係と判定し、検出できない |

単純な同一ファイル内の検索ではgrepと大差ないが、**exportのalias解決を伴うクロスファイルの呼び出し関係の追跡では、1回のクエリで複数ファイルの手動Readを省略できた。** 一方、重複コード検出や「呼び出し側で見た名前からの逆引き」はgrepでも苦手な部分はあるが、codegraphも解決しておらず、過大な期待は禁物。

## まとめ

- 導入・インデックス構築は高速(159ファイル・2.6秒)でAPIキー・GPU不要という触れ込みは正確だった。
- 単純な同一ファイル内の呼び出し関係は正確。
- クロスファイルのexport alias解決は、grepでは追いにくいケースで明確に優位性を確認できた(`_q`↔`quote`)。
- 一方、宣言時の元の名前でしか検索できない(呼び出し側の名前`quote`では見つからない)という制約も確認した。
- Qiita記事が報告した「独立に再実装された重複コードを検出できない」という限界は、自作の最小ケースで再現を確認した。これはグラフベース(呼び出し/参照関係)の設計に由来する本質的な限界であり、ツールのバグではない。
- 汎用的なシンボル名(`main`)では無関係な結果が多数混入する。
