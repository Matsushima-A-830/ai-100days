# Day 060 検証結果: colbymchenry/codegraph

- 出典: https://github.com/colbymchenry/codegraph (MIT License)
- バージョン: 1.6.4 (`npx -y @colbymchenry/codegraph version`)
- 検証対象: 本リポジトリ (ai-100days) 自身
- 検証環境: 1〜5章はRoutineクラウド実行環境(GPUなし。npm registryへの到達は可能だった)。6章はローカルPC(WSL2 / Node.js v26.8.2 / npx 11.19.1)での再現

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

## 6. ローカル検証(人間のPC)

- 日付: 2026-11-27
- 環境: WSL2 (Linux 6.6.87.2) / Node.js v26.8.2 / npx 11.19.1 / codegraph 1.6.4(`npx -y @colbymchenry/codegraph@1.6.4`で版を固定)
- 対象: Day 059(heretic)をマージした後のmainに本ブランチを取り込んだコミットを`git archive HEAD`で作業ディレクトリ(`$WORK`)に展開したもの。未追跡のローカルファイルを索引に混ぜないため
- Day番号の変更: Day 059はhereticとしてPR #204でマージ済みのため、本検証をDay 060へ変更した(`experiments/day-059`→`experiments/day-060`など)。1〜5章のログ中のパス`experiments/day-059/...`も`day-060`に置換している
- ログ: `local/`(作業ディレクトリのパスは`$WORK`に置換)

### 6-1. 再現結果

| 項目 | PR(1〜5章) | ローカル |
|---|---|---|
| `init` | 159ファイル、2,162ノード、4,700エッジ、2.6秒 | 163ファイル、2,198ノード、4,738エッジ、2.1秒(`real 0m8.882s`。初回の`npx`ダウンロード込み) |
| `callers render_frame` | `main`(render.py:525, 549) | 同じ |
| `callees render_frame` | chrome / scene_architecture / caption / FADE / SCENES | 同じ |
| `callers _q` | main.js:22、pricing.js:30 | 同じ |
| `callers quote` | `Symbol "quote" not found — did you mean: cols, urllib.parse?` | 同じ |
| `impact` / `callers validate_email_signup` | a.py:1のみ / 0件 | 同じ(`impact check_email_format`もb.py:1のみ) |
| `context "refactor email validation ..."` | validate_email_signup + day-035の`OnEnable`、`Low-confidence match` | 同じ |
| `explore render_frame main` | day-021・day-025などの無関係な`main`が混入 | 同じ(531行) |

ファイル数の差(159→163)は、PR作成後にDay 059(heretic)の成果物がmainに入ったため。DB 7.40 MB。

ソースとの照合もローカルで行った。

```
$ grep -n "render_frame\|^def main" tools/video/render.py
456:def render_frame(spec, segs, i_seg, t, total, cap_text) -> Image.Image:
491:def main():
525:            render_frame(spec, segs, i, t, total, frame_state(segs, t)[1]).save(args.stills / f"seg{i:02d}.png")
549:            last_bytes = render_frame(spec, segs, i, t, total, cap).tobytes()
$ grep -n quote experiments/day-010/sample-app/main.js
4:const { quote, debugSnapshot } = require('./lib/pricing');
22:  return quote(String(code || ''), Number(subtotal) || 0);
```

### 6-2. 追加確認: `query`/`node`でも呼び出し側の名前では引けない

`callers`以外のシンボル検索でも`quote`を試した。

```
$ codegraph query quote
Search Results for "quote":
variable    cols
  experiments/day-022/prepare_data.py:7
import      urllib.parse
  experiments/day-017/installed-skills/literature-review/scripts/verify_citations.py:14
$ codegraph node quote
**cols** (variable)
**Location:** experiments/day-022/prepare_data.py:7
```

`query`は文字列`quote`を含む無関係なシンボル(`quote_volume`を含む配列、`from urllib.parse import quote`)を返し、`node`はその1件目(`cols`)を表示した。exportのalias名`quote`から`_q`に辿る手段はCLIには無かった。

### 6-3. 追加確認: 利用統計(テレメトリ)が既定で有効

初回の`init`で次の表示が出た(1章の`init-log.txt`にも同じ行がある)。

```
codegraph collects anonymous usage stats (no code, paths, or names) — "codegraph telemetry off" or CODEGRAPH_TELEMETRY=0 disables.
```

`~/.codegraph/telemetry.json`は`"enabled": true, "consent_source": "default-notice"`で、オプトアウト方式だった。`init`・`version`の2回を実行した時点の送信待ちキュー(`~/.codegraph/telemetry-queue.jsonl`)の中身は次の2行で、コマンド名と回数だけだった。

```
{"v":2,"d":"2026-11-27","k":"cli_command","n":"init","c":1,"e":0}
{"v":2,"d":"2026-11-27","k":"cli_command","n":"version","c":1,"e":0}
```

`codegraph telemetry off`を実行すると`✓ Telemetry disabled. Buffered, unsent data was deleted.`と表示され、キューのファイルが消えた。以降のコマンドはすべて`CODEGRAPH_TELEMETRY=0`付きで実行した。送信先との通信そのもの(何がいつ送られたか)は観測していない。

### 6-4. 追加確認: リポジトリへの書き込み

`init`後に展開元(`git archive HEAD`)と作業ディレクトリを`diff -rq`で比べると、差分は`.codegraph/`だけだった(中に`*`と`!.gitignore`を書いた`.gitignore`が自動生成される)。`CLAUDE.md`や`.mcp.json`などの設定ファイルは`init`では作られなかった。ルートの`.gitignore`への`.codegraph/`追記は、自動生成の`.gitignore`があるため必須ではないが、害は無いので残した。

### 6-5. まとめ

PR(1〜5章)の結果は、インデックス規模の差(ファイル追加分)を除いてすべてローカルで再現した。追加で、(1) `query`/`node`でもalias名からは辿れないこと、(2) 匿名の利用統計がオプトアウト方式で既定有効であることを確認した。
