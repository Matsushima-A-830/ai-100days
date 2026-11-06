# Day 039 検証結果 — vercel-labs/agent-browser & agent-desktop

実行環境: Claude Code Routine クラウドコンテナ (Linux, Node v22.23.4, npm 10.9.9)。
検証日: 2026-11-06。

## 1. agent-browser の導入

```
$ npm install agent-browser
added 1 package in 866ms
$ cat node_modules/agent-browser/package.json | grep '"version"'
  "version": "0.27.0",
```

npmのdist-tagsを確認すると `latest` は `0.41.2`。

```
$ npm view agent-browser dist-tags --json
{
  "latest": "0.41.2"
}
```

バージョン指定なしの `npm install agent-browser` では **latestタグの0.41.2ではなく
0.27.0が入った**(14バージョンも古い)。`npm install agent-browser@latest` と明示すると
期待通り0.41.2が入る(EBADENGINE警告は出るがインストール自体は成功):

```
$ npm install agent-browser@latest
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: 'agent-browser@0.41.2',
npm warn EBADENGINE   required: { node: '>=24.0.0', pnpm: '>=11.0.0' },
npm warn EBADENGINE   current: { node: 'v22.23.4', npm: '10.9.9' }
npm warn EBADENGINE }
added 1 package, and audited 2 packages in 2s
```

原因を特定するため各バージョンの`engines`を比較した:

```
$ npm view agent-browser engines
{ node: '>=24.0.0', pnpm: '>=11.0.0' }
$ npm view agent-browser@0.27.0 engines
(出力なし = engines未指定)
$ npm view agent-browser@0.40.0 engines
{ node: '>=24.0.0', pnpm: '>=11.0.0' }
```

`--loglevel silly`で内部ログを見ると、バージョン未指定のインストールは
`agent-browser@*`というsemver範囲として解決されていた:

```
$ npm install agent-browser --loglevel silly 2>&1 | grep "fetch manifest"
npm silly fetch manifest agent-browser@*
```

つまり `npm install agent-browser` は内部的に `*` 範囲として解決され、その際npmは
現在のNode(v22.23.4、Node 24未満)の`engines.node`要件を満たさない0.41.x系・0.40.x系
を候補から除外し、engines未指定の古い0.27.0を選んだ。一方 `@latest` や `@<version>`
のように明示指定した場合はこの範囲フィルタを経ないため最新版がそのまま入る。
**公式READMEの `npm install -g agent-browser` の手順通りに実行すると、Node 24未満の
環境では最も古いバージョンが黙って入り、エラーも出ない。** これは本検証環境固有の
制約ではなく、Node 24を使っていない読者が自分のPCでも再現する落とし穴のため記事の主役
にする。

再現したバージョン: `agent-browser 0.41.2`(`@latest`指定でインストール後に確認)。

## 2. agent-browserのコア操作(open/snapshot/fill/click/read)

このクラウド実行環境のネットワークポリシーでは `example.com` や `www.google.com` 等の
一般的な外部サイトへの接続が拒否される(エージェントプロキシのステータスで
`gateway answered 403 to CONNECT` を複数回確認。例: `example.com:443`,
`www.google.com:443`)。これは検証対象のagent-browser自体の問題ではなく本環境の
ネットワーク許可リストによる制約なので、ローカルに検証用ページ(日本語のフォーム+
リンク一覧。`testsite/index.html`参照)を立てて代わりに検証した。

```
$ python3 -m http.server 8931 --bind 127.0.0.1 &
$ agent-browser open http://127.0.0.1:8931/
✓ テスト用検索フォーム
  http://127.0.0.1:8931/
```

`snapshot`はアクセシビリティツリーを`@ref`付きで返す(`ref=e7`がテキスト入力欄、
`ref=e8`が検索ボタン):

```
$ agent-browser snapshot
- navigation
  - link "Home" [ref=e2]
  ...
- main
  - heading "検索フォーム" [level=2, ref=e5]
  - form
    - textbox "キーワード:" [ref=e7]
    - button "検索" [ref=e8]
  ...
```

`@ref`を使った `fill` → `click` で実際にフォームへ入力・送信できた。送信後の
`snapshot`に検索結果の反映(JSによるDOM更新)が正しく現れている:

```
$ agent-browser fill @e7 "AIエージェント 比較"
✓ Done
$ agent-browser click @e8
✓ Done
$ agent-browser snapshot
...
    - textbox "キーワード:" [ref=e7]: AIエージェント 比較
    - button "検索" [ref=e8]
  - paragraph
    - StaticText "検索結果: "
    - StaticText "AIエージェント 比較"
...
```

`read`コマンドは整形済みのMarkdown風テキストを返す(見出し・リンク・リストが
読みやすく変換されている)。全コマンドとも**正常に動作した**。

## 3. トークン消費量の自分の実測(公式の「約90%削減」とは別物)

公式主張(Playwright MCP比で約90%少ないトークン消費)を自分の手元で簡易再現するため、
同じローカルページについて「生HTML」と「agent-browserのsnapshot出力」の文字数を比較した。
(厳密なトークナイザでの比較は、tiktokenのボキャブラリファイルのダウンロード先ホストが
本環境のネットワークポリシーで拒否されたため断念し、文字数を代理指標として使った。)

```
$ curl -s http://127.0.0.1:8931/ > raw_page.html
$ agent-browser snapshot > snapshot_output.txt
$ wc -c raw_page.html snapshot_output.txt
  1738 raw_page.html
   974 snapshot_output.txt
```

(`wc -c`はバイト数。日本語を含むUTF-8のため文字数とはずれる。Pythonで文字数も計測):

```
raw chars: 1526
snap chars: 785
reduction: 48.6%
```

**自分の簡易ページでの実測では約48.6%の削減**だった。公式の「約90%」はPlaywright MCPの
出力形式との比較であり、今回は素のHTML(`curl`で取得した生のレスポンス)との比較という
前提が異なる上、検証ページも小さく実際のWebアプリよりずっと単純なため、数値は参考値に
留まる。ただし「スクリーンショットではなくテキスト化されたアクセシビリティツリーの方が
軽量」という方向性自体は、この簡易な比較でも確認できた。

## 4. agent-desktop

```
$ npm install agent-desktop@latest
$ agent-desktop --version
agent-desktop 1.2.0
$ agent-desktop status
{"version":"2.6","ok":true,"command":"status","data":{"permissions":{"accessibility":
{"state":"denied","suggestion":"No D-Bus session bus is reachable. Run inside a desktop
session, or start one with 'dbus-run-session -- <command>'."},"automation":
{"state":"not_required"},"screen_recording":{"state":"unknown"}},"platform":"linux",
...}}
```

提案に従い `dbus-run-session` 経由でも試したが、今度は別の理由で拒否された:

```
$ dbus-run-session -- agent-desktop status
...
"accessibility":{"state":"denied","suggestion":"AT-SPI is not installed or not visible
to this process. Install the at-spi2-core package, then retry. Inside Flatpak add
'--talk-name=org.a11y.Bus'; inside snap connect the 'desktop-legacy' or 'unity7'
interface."}
```

**Routine環境の制約により未検証、ローカル検証待ち。**(このクラウドコンテナには
ディスプレイ・ウィンドウマネージャ・AT-SPIアクセシビリティバスが存在せず、GUI操作系の
コマンドは検証できない。`status`でのプラットフォーム判定("platform":"linux")自体は
正常に動作した。)
