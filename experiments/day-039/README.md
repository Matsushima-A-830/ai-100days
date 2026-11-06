# Day 039 — vercel-labs/agent-browser & agent-desktop 再現手順

出典:
- https://github.com/vercel-labs/agent-browser (Apache-2.0)
- https://github.com/vercel-labs/agent-desktop (Apache-2.0)

## 1. agent-browser の導入とバージョン落とし穴の再現

```bash
mkdir day039-work && cd day039-work
npm install agent-browser         # バージョン指定なし
cat node_modules/agent-browser/package.json | grep version
# => "version": "0.27.0"  (registryのdist-tags.latestは0.41.2なのに古いバージョンが入る)

npm view agent-browser dist-tags --json
# => {"latest": "0.41.2"}

npm install agent-browser@latest  # @latestを明示すると最新が入る
cat node_modules/agent-browser/package.json | grep version
# => "version": "0.41.2"
```

原因確認:

```bash
npm view agent-browser engines        # => { node: '>=24.0.0', pnpm: '>=11.0.0' }
npm view agent-browser@0.27.0 engines # => (出力なし。engines未指定)
npm install agent-browser --loglevel silly 2>&1 | grep "fetch manifest"
# => npm silly fetch manifest agent-browser@*
```

バージョン指定なしの `npm install agent-browser` は内部的に `agent-browser@*` という
semver範囲として解決される。npmはこの範囲解決時、現在のNode(今回はv22.23.4)の
`engines.node`要件を満たさないバージョンを候補から除外するため、
`engines.node: ">=24.0.0"` を要求する0.41.2系は除外され、engines未指定の0.27.0が
選ばれる。一方 `@latest` や `@0.41.2` のように明示的にバージョン/タグを指定した場合は
この範囲解決を経ないため、`EBADENGINE`警告は出るがそのまま最新版がインストールされる。

## 2. agent-browser のコア操作(open/snapshot/fill/click/read)

ネットワーク越しの実サイトはこの検証環境のネットワークポリシーで到達できないため、
ローカルに検証用の静的ページ(日本語フォーム+リンク一覧)を立てて操作した。

```bash
cd testsite && python3 -m http.server 8931 --bind 127.0.0.1 &

agent-browser open http://127.0.0.1:8931/
agent-browser snapshot
agent-browser fill @e7 "AIエージェント 比較"
agent-browser click @e8
agent-browser snapshot   # フォーム送信後の結果が反映されているか確認
agent-browser read       # 整形済みテキストの取得
```

テストページのソースは `testsite/index.html` 相当(本README作成環境のスクラッチ領域に
作成。内容は results.md に抜粋を記録)。

## 3. 文字数(簡易トークン量の代理指標)比較

```bash
curl -s http://127.0.0.1:8931/ > raw_page.html
agent-browser open http://127.0.0.1:8931/ > /dev/null
agent-browser snapshot > snapshot_output.txt
wc -c raw_page.html snapshot_output.txt
```

## 4. agent-desktop

```bash
npm install agent-desktop@latest
agent-desktop --version      # => agent-desktop 1.2.0
agent-desktop status
# => accessibility.state: "denied", suggestion: "No D-Bus session bus is reachable..."

dbus-run-session -- agent-desktop status
# => accessibility.state: "denied", suggestion: "AT-SPI is not installed or not
#    visible to this process. Install the at-spi2-core package, then retry..."
```

この実行環境(クラウドのヘッドレスコンテナ)にはディスプレイ・ウィンドウマネージャ・
AT-SPI(Linuxのアクセシビリティバス)が存在しないため、`status`コマンドでの
プラットフォーム判定("platform":"linux")自体は正常に動くが、実際のGUIアプリ操作
(snapshot/click等)はこの環境では検証できない。**ローカル検証が必要。**

ローカルPC(GUI/デスクトップ環境あり)での再現手順:

```bash
npm install agent-desktop@latest
agent-desktop status   # accessibility.state が "granted" になるか確認
                        # macOSは初回にアクセシビリティ権限の許可ダイアログが出る想定
agent-desktop snapshot --app <適当なGUIアプリ名>
agent-desktop find --text "<適当な文字列>"
agent-desktop click @e1   # 等、実際の要素を操作
```
