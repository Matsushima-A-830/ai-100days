---
title: "AIエージェント用ネット接続ツールAgent-Reachを実機で検証した"
emoji: "🌐"
type: "tech"
topics: ["ai", "agent", "cli", "github", "oss"]
published: false
---

AIエージェントにログイン不要でWeb/GitHub/YouTube/Bilibili/V2EXへのアクセスを与えるCLI「[Agent-Reach](https://github.com/Panniantong/Agent-Reach)」(MIT、Panniantong)を実際にインストールし、ログイン不要チャンネルの動作、素のcurlでは読めないページをどう読めるようにするか、ヘルプ文言と実際の挙動の食い違いまでを確認した。

## Agent-Reachとは何か

Agent-Reachは、AIエージェントに「インターネットへの実際のアクセス手段」を与えるCLIツールである。GitHub・YouTube・Bilibili・V2EX・Webという5つのチャンネルがデフォルトで有効になっており、READMEによればこのうちGitHub・V2EX・Bilibili(字幕を除く)はログイン不要で使える設計になっている。すべての出力はJSONで返るため、エージェントが解析しやすい。

この連載では当初、クラウドの無人実行環境でのインストールを試みたが、公式インストーラ・PyPI・公式リリースからの`uv tool install`という3つの方法すべてが、無人実行環境固有の安全装置(外部コードの実行をブロックするClaude Codeの分類器)に拒否された。これはAgent-Reach自体の不具合ではなく実行環境側の制約だったため、人間のローカルPC(通常のインターネット接続、WSL2 Ubuntu 24.04.3)で改めて検証した。

## インストール: 公式手順通りに一発で成功

```bash
$ uv tool install https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
```

```
Resolved 14 packages in 135ms
      Built agent-reach @ https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
Installed 14 packages in 38ms
 + agent-reach==1.6.0 (from https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip)
Installed 1 executable: agent-reach
```

クラウドの無人実行環境で3つの方法すべてがブロックされていたインストールが、ローカルPCでは一発で成功した。`agent-reach setup`を実行すると、デフォルトで有効な5チャンネルすべてが`ok: true`を返し、エージェント向けスキルファイルもインストールされた。`agent-reach doctor`では各チャンネルが`status: unverified`(設定済みだが未検証)と表示され、実際に動くかどうかは個別にコマンドを叩いて確認する必要があった。

## つまずいた点: READMEのコマンド文法が実際とは違っていた

READMEのQuick Startには`agent-reach get github read yt-dlp/yt-dlp`のような`get`という動詞を挟む表記があったが、これをそのまま実行すると失敗する。

```bash
$ agent-reach get github read yt-dlp/yt-dlp
```

```
{"ok": false, "error": {"code": "BAD_INPUT", "message": "unknown command or channel: get"}}
```

`agent-reach help`で確認したところ、正しい文法は`agent-reach <channel> <action> [args]`で、`get`という動詞は存在しない。

```bash
$ agent-reach github read yt-dlp/yt-dlp
```

```
{"ok": true, "channel": "github", "action": "read", "backend": "gh",
 "items": [{"title": "yt-dlp/yt-dlp", "text": "<!-- MANPAGE: ... -->\n...(README全文)..."}]}
```

ログイン・APIキーなしで、READMEの全文をクリーンなJSONとして取得できた。V2EX(`agent-reach v2ex hot`)とBilibili(`agent-reach bilibili search "大模型"`)も同様にログイン不要で実際に動作し、それぞれ実際のトピック本文・検索結果を取得できた。

## Before/After: GitHub issueページ

通常のcurlでは読みにくいページとして、コメント数の多いGitHub issue([yt-dlp/yt-dlp#6539](https://github.com/yt-dlp/yt-dlp/issues/6539)、コメント167件)を選び、素のcurlとAgent-Reach経由を比較した。

```bash
$ curl -sL "https://github.com/yt-dlp/yt-dlp/issues/6539" | head -c 300
```

```
<!DOCTYPE html>
<html lang="en" ...>
<script type="importmap">{"imports":{"react":"https://github.githubassets.com/assets/react-...
```

GitHubのissueページはクライアントサイドレンダリング(React)のため、素のHTMLには本文もコメントも含まれておらず、人間にもエージェントにもそのままでは読めない。

```bash
$ agent-reach github read "https://github.com/yt-dlp/yt-dlp/issues/6539"
```

```
{"ok": true, "channel": "github", "action": "read", "backend": "gh",
 "items": [{"title": "CeskaTelevize broken", "author": "jirih",
   "text": "### DO NOT REMOVE OR SKIP THE ISSUE TEMPLATE\n...(issue本文全文)...",
   "raw": {"comments": 167, "is_pull_request": false}}]}
```

issue本文はクリーンなMarkdownテキストとして確実に取得できた。なお、issue参照には`owner/repo#N`のような短縮形は使えず、フルURLを渡す必要があることも試行の中で分かった。

## 発見: 「with comments」はコメント件数のみを指していた

`agent-reach channels`のヘルプ文には、`github read`が「Read a repository (with README) or an issue / PR (with comments)」(コメント付きで読む)と説明されている。しかし実際に取得した`items`は issue本文1件のみで、`raw.comments`の中身はコメント本文の配列ではなく**コメント件数を示す整数(167)**だった。つまり「with comments」という表現は「コメント数を把握できる」という意味合いであり、コメント本文そのものを一括取得できるわけではなかった。これは実際に手を動かして初めて分かった、ヘルプ文言と実装のギャップである。

## YouTube字幕: プラットフォーム側のレート制限に遭遇

YouTube字幕取得(`agent-reach youtube subtitle <id>`)も試したが、実行するとYouTube側からHTTP 429(Too Many Requests)が返ってきた。

```
$ agent-reach youtube subtitle WdZjoMi6W7Y
{"ok": false, "error": {"code": "RATE_LIMITED",
  "message": "yt-dlp exited 1: ... HTTP Error 429: Too Many Requests"}}
```

別の動画IDで再試行しても同じくレート制限がかかり、2回目は約1時間のクールダウンがローカルに記録されていた。これはAgent-Reachのバグではなく、内部で使われている`yt-dlp`に対するYouTube側の実際のレート制限であり、Agent-Reachはそれを検知して無駄なリトライをせず正直にエラーを返している。

## まとめ

- クラウドの無人実行環境で3つの方法すべてがブロックされていたインストールは、ローカルPCでは公式手順通り一発で成功した。これは実行環境固有の制約であり、Agent-Reach自体の不具合ではないことが確定した。
- GitHub・V2EX・Bilibiliというログイン不要チャンネルは、実際にコマンドを叩いて動作を確認できた。
- GitHubのissueページは素のcurlでは本文すら読めないが、Agent-Reach経由ではissue本文を確実に読める、という核心的な差を実機で確認した。
- READMEが示す`get`を挟むコマンド文法、issue参照の短縮形(`owner/repo#N`)はいずれも実際には動かず、正しい文法(`agent-reach <channel> <action>`、フルURL指定)を確認する必要があった。
- ヘルプ文言の「with comments」は、実際にはコメント件数のみを返し、コメント本文そのものは取得できないという、ヘルプと実装の小さなギャップが見つかった。
- YouTube字幕取得では、検証中にYouTube側の実際のレート制限に遭遇した。
- 追加の有料APIキーは不要、GPUも不要だった。

## 出典・ライセンス

- リポジトリ: https://github.com/Panniantong/Agent-Reach (MIT)
- 検証コード・実行ログの全文は[GitHubリポジトリのexperiments/day-029](https://github.com/Matsushima-A-830/ai-100days/tree/main/experiments/day-029)を参照。
