---
title: "Vercel Labsのagent-browserを試す: アクセシビリティツリーでAIエージェントがブラウザを操作する"
emoji: "🌳"
type: "tech"
topics: ["ai", "llm", "browser", "accessibility", "claudecode"]
published: false
---

## 概要

Vercel Labsが公開している[agent-browser](https://github.com/vercel-labs/agent-browser)(Apache-2.0)は、AIエージェントにブラウザ操作をさせるためのRust製CLIである。
スクリーンショットをVLM(視覚言語モデル)に渡す方式ではなく、ブラウザのアクセシビリティスナップショットをテキスト/JSON化し、各要素に`@e1`のような参照(ref)を振って、エージェントがその参照IDを指定して`click`や`fill`を呼ぶ、という方式を取る。
Playwright MCP比で約90%少ないトークン消費を主張している。

姉妹ツールの[agent-desktop](https://github.com/vercel-labs/agent-desktop)(同じくApache-2.0)は同じ発想をOSのデスクトップ操作に広げたもので、2026年11月5日時点のGitHub Trendingで新着ながら2,173star/日という伸びを見せていた。

筆者はこのagent-browserを実際に導入し、Claude Code自身をドライバーとしてローカルの検証用ページを操作し、公式が主張するトークン削減効果を自分の手元で簡易的に測った。
導入コマンドそのままでは最新版が入らないという落とし穴にも遭遇したので、それも含めて記録する。

- 出典: https://github.com/vercel-labs/agent-browser (Apache-2.0)
- 出典: https://github.com/vercel-labs/agent-desktop (Apache-2.0)
- 日本語記事件数(2026-11-05時点、Zenn/Qiita/note検索): 0件(個人技術ブログに1本あるがZenn/Qiita/note本体への掲載は未検出)

## 導入: `npm install agent-browser` だけでは最新版が入らない

公式READMEに従って導入しようとすると、最初の一歩でつまずいた。

```
$ npm install agent-browser
added 1 package in 866ms
$ cat node_modules/agent-browser/package.json | grep '"version"'
  "version": "0.27.0",
```

npmのレジストリで`latest`タグを確認すると`0.41.2`のはずだった。

```
$ npm view agent-browser dist-tags --json
{
  "latest": "0.41.2"
}
```

バージョン未指定の`npm install agent-browser`では、latestタグの0.41.2ではなく14バージョンも古い0.27.0が、エラーも警告も出さずに入った。
`npm install agent-browser@latest`のようにバージョンを明示すると、期待通り0.41.2が入る(EBADENGINEという警告は出るがインストール自体は成功する)。

```
$ npm install agent-browser@latest
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: 'agent-browser@0.41.2',
npm warn EBADENGINE   required: { node: '>=24.0.0', pnpm: '>=11.0.0' },
npm warn EBADENGINE   current: { node: 'v22.23.4', npm: '10.9.9' }
npm warn EBADENGINE }
```

原因を調べるため各バージョンの`engines`フィールドを比較した。

```
$ npm view agent-browser engines
{ node: '>=24.0.0', pnpm: '>=11.0.0' }
$ npm view agent-browser@0.27.0 engines
(出力なし。engines未指定)
```

最新の0.41.2系はNode 24以上を要求するが、古い0.27.0にはこの制約が無い。
`--loglevel silly`で内部挙動を見ると、バージョン未指定のインストールは`agent-browser@*`というsemver範囲の解決として処理されていた。

```
$ npm install agent-browser --loglevel silly 2>&1 | grep "fetch manifest"
npm silly fetch manifest agent-browser@*
```

つまり`*`のような範囲指定でインストールする際、npmは現在のNodeバージョンの`engines.node`要件を満たさない候補を除外してから選ぶため、Node 24未満の環境では`engines`未指定の古いバージョンが選ばれてしまう。
一方、`@latest`や`@<version>`のように明示的に指定した場合はこの範囲フィルタを経由しないため、素直に最新版が入る。

Node 24は2026年時点でもまだ広く普及したバージョンとは言えず、Node 22や20を使っている読者は少なくないはずだ。
**公式READMEの`npm install -g agent-browser`をそのまま実行すると、エラーも警告も出さずに古いバージョンが入ってしまう**ので、導入時は`npm install agent-browser@latest`のようにバージョンを明示することを勧める。

## アクセシビリティツリーでの操作を実際に動かす

このクラウド実行環境のネットワークポリシーでは一般的な外部サイト(`example.com`や`www.google.com`など)への接続が拒否されたため、ローカルに日本語のフォームとリンク一覧を持つ検証用ページを立てて操作した。

```
$ agent-browser open http://127.0.0.1:8931/
✓ テスト用検索フォーム
  http://127.0.0.1:8931/
```

`snapshot`コマンドで、ページの構造がアクセシビリティツリーとして`@ref`付きで返ってくる。

```
$ agent-browser snapshot
- navigation
  - link "Home" [ref=e2]
  - link "About" [ref=e3]
  - link "Contact" [ref=e4]
- heading "agent-browser 検証用ページ" [level=1, ref=e1]
- main
  - heading "検索フォーム" [level=2, ref=e5]
  - form
    - textbox "キーワード:" [ref=e7]
    - button "検索" [ref=e8]
  - heading "記事一覧" [level=2, ref=e6]
  - list
    - listitem [level=1]
      - link "AIエージェントの最新動向" [ref=e9]
...
```

HTMLのタグ構造やCSSクラス名、スタイル情報は含まれず、「何がどこにあり、どう操作できるか」という情報だけが残っている。
この`@ref`を使って`fill`→`click`を呼ぶと、実際にフォームへ入力して送信できた。

```
$ agent-browser fill @e7 "AIエージェント 比較"
✓ Done
$ agent-browser click @e8
✓ Done
```

送信後に`snapshot`を取り直すと、JavaScriptによるDOM更新(検索結果の表示)が正しく反映されていた。

```
    - textbox "キーワード:" [ref=e7]: AIエージェント 比較
    - button "検索" [ref=e8]
  - paragraph
    - StaticText "検索結果: "
    - StaticText "AIエージェント 比較"
```

座標やピクセルを一切扱わず、意味のある参照IDだけでクリックや入力ができる点は、LLMにとって扱いやすい設計だと感じた。

## 「約90%少ない」トークン消費を自分でも測ってみる

公式は「Playwright MCP比で約90%少ないトークン消費」を主張している。
筆者の手元では厳密なトークナイザでの比較まではできなかった(後述の制約のため文字数で代用した)が、同じページについて「素のHTML」と「agent-browserのsnapshot出力」の文字数を比較した。

```
$ curl -s http://127.0.0.1:8931/ > raw_page.html
$ agent-browser snapshot > snapshot_output.txt
$ wc -c raw_page.html snapshot_output.txt
  1738 raw_page.html
   974 snapshot_output.txt
```

Pythonで文字数(バイト数ではなく)を数えると次の通り。

```python
raw chars: 1526
snap chars: 785
reduction: 48.6%
```

**自分の簡易ページでの実測は約48.6%の削減**だった。
公式の約90%とは前提が異なる(公式はPlaywright MCPの出力形式との比較であり、今回は生のHTMLレスポンスとの比較)うえ、検証ページも小さく実際のWebアプリよりずっと単純なので、この数字はあくまで参考値である。
それでも「スタイルやタグ構造を削ぎ落とし、意味のある構造だけをテキスト化する」という方向性の効果自体は、この簡易な比較でも確認できた。

## 検証できなかった部分: agent-desktop

姉妹ツールのagent-desktopも導入し、`status`コマンドでプラットフォーム判定までは確認できた(`"platform":"linux"`)。
ただし実際のGUIアプリを操作する部分は**この検証環境では確認できておらず、ローカル検証が必要**。
再現手順はPRの説明文と`experiments/day-039/README.md`にまとめてある。

## まとめ

- agent-browserは実際に`open`→`snapshot`→`fill`→`click`→`read`という一連の操作が問題なく動き、アクセシビリティツリーベースの操作性を確認できた。
- 公式READMEのインストール手順(`npm install agent-browser`)は、Node 24未満の環境ではエラーも警告も出さずに古いバージョンが入ってしまう落とし穴がある。`@latest`を明示することを勧める。
- トークン消費量の削減について、自分の簡易な比較では約48.6%(公式の約90%とは前提が異なる参考値)だったが、方向性自体は確認できた。
