# Day 029 結果: Agent-Reach (Panniantong/Agent-Reach)

検証対象: https://github.com/Panniantong/Agent-Reach (MIT)
検証環境: Windows 11 + WSL2 Ubuntu 24.04.3、`agent-reach` 1.6.0

## 0. クラウドRoutine環境での試行(前回PR, Routine環境固有の制約)

前回のPRで、クラウドRoutine環境において、公式推奨のインストール手順を含む3つの方法すべてが
Claude Codeの「autoモード分類器」にブロックされ、`agent-reach`本体を一度も実行できなかった
(詳細はREADME.md参照)。これはAgent-Reach自体の不具合ではなく、無人実行(Routine)環境固有の
サンドボックス安全装置によるものだった。

## 1. ローカルPCでのインストール: 公式手順通りに成功

人間のローカルPC(通常のターミナル権限)で、READMEが推奨する手順をそのまま実行した。

```
$ uv tool install https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
Resolved 14 packages in 135ms
      Built agent-reach @ https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
Installed 14 packages in 38ms
 + agent-reach==1.6.0 (from https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip)
 ...
Installed 1 executable: agent-reach
```

クラウドRoutine環境で3つの方法すべてがブロックされていたインストールが、ローカルPCでは
一発で成功した。これは前回PRの判断(Routine環境固有の制約であり、Agent-Reach自体の問題では
ない)を裏付ける結果である。

## 2. セットアップとdoctor

```
$ agent-reach setup
```

`setup`は、デフォルトで有効な5チャンネル(github・youtube・bilibili・v2ex・web)すべてに
ついて`ok: true`を返し、エージェント向けスキル(`SKILL.md`)もインストールした。実行結果の
JSONには、各チャンネルについて「ログイン無しで何ができるか」を一覧化した日本語ではなく
中国語の`capability_summary`が含まれており、GitHub・V2EX・Bilibili(字幕以外)・Webは
ログイン不要で動作する設計であることが、ツール自身の自己申告として確認できた。

```
$ agent-reach doctor
```

全チャンネルが`status: unverified`(＝設定は完了しているが、まだ実際にアクセスを試していない
状態)と表示された。`doctor`はネットワークアクセスを行わない静的チェックであり、実際に
動くかどうかは個別に`agent-reach <channel> <action>`を呼んで確認する必要があった。

## 3. ログイン不要チャンネルを実際に叩いた結果

### 3-1. GitHub: README読み取り(成功)

```
$ agent-reach github read yt-dlp/yt-dlp
{"ok": true, "channel": "github", "action": "read", "backend": "gh", "items": [
  {"title": "yt-dlp/yt-dlp", "url": "https://github.com/yt-dlp/yt-dlp", ...
   "text": "<!-- MANPAGE: BEGIN EXCLUDED SECTION -->\n...(README全文)..."}
]}
```

ログイン・APIキーなしで、READMEの全文をクリーンなJSONとして取得できた。

### 3-2. V2EX: 人気トピック取得(成功)

```
$ agent-reach v2ex hot
{"ok": true, "channel": "v2ex", "action": "hot", "backend": "v2ex-api", "items": [
  {"title": "深夜求助，物业只提前 1 小时通知停电，导致我家里电脑坏了", ...}
  ...
]}
```

ログイン不要で、実際のトピック本文(中国語)まで正しく取得できた。

### 3-3. Bilibili: 動画検索(成功)

```
$ agent-reach bilibili search "大模型"
{"ok": true, "channel": "bilibili", "action": "search", "backend": "bili-cli", "items": [
  {"title": "【全748集】目前B站最全最细的AI大模型零基础全套教程...", "author": "大模型官方课程", ...}
  ...
]}
```

ログイン不要で検索結果(タイトル・作者・再生数)が取得できた。

### 3-4. YouTube字幕: platformのレート制限で失敗(正直に記録)

```
$ agent-reach youtube subtitle WdZjoMi6W7Y
{"ok": false, "error": {"code": "RATE_LIMITED",
  "message": "yt-dlp exited 1: ERROR: Unable to download video subtitles for 'zh-Hans': HTTP Error 429: Too Many Requests"}}

$ agent-reach youtube subtitle 3TwbE7gv6qo   # 別の動画で再試行
{"ok": false, "error": {"code": "RATE_LIMITED", "message": "Platform reported a rate limit",
  "hint": "Wait 3586 seconds before retrying this channel."}}
```

1回目の呼び出しでYouTube側から429(Too Many Requests)を返され、Agent-Reachはそれを検知して
このチャンネルを約1時間ロック(2回目の呼び出しは、サーバーに再度問い合わせることなく
ローカルに記録したクールダウン情報を見て即座に拒否を返した)した。これは**ツールのバグでは
なく、YouTube側のレート制限をAgent-Reachが正直に伝え、無駄なリトライで状況を悪化させない
よう自衛した挙動**だと判断する。実際にこの制約にぶつかった以上、本体験として正直に記録する。

### 3-5. 汎用`read <url>`コマンド(成功)

```
$ agent-reach read "https://v2ex.com/t/1252074"
{"ok": true, "channel": "v2ex", "action": "read", "backend": "v2ex-api", ...}
```

URLを渡すだけでチャンネルを自動判定して読み取る`read`コマンドも、V2EXで正しく動作した。

## 4. Before/After比較: GitHub issueページ

今日の計画通り、通常のcurl/Web検索ではそのまま読みにくいページとして、コメント数の多い
GitHub issue(yt-dlp/yt-dlp#6539、コメント167件)を選び、素のcurlとAgent-Reach経由を比較した。

**Before(素のcurl)**:

```
$ curl -sL "https://github.com/yt-dlp/yt-dlp/issues/6539" | head -c 1000
<!DOCTYPE html>
<html lang="en" ...>
<script type="importmap">{"imports":{"react":"https://github.githubassets.com/assets/react-...
```

GitHubのissueページはクライアントサイドレンダリング(React)のため、素のHTMLには本文も
コメントも含まれておらず、人間にもエージェントにもそのままでは読めない。

**After(Agent-Reach経由)**:

```
$ agent-reach github read "https://github.com/yt-dlp/yt-dlp/issues/6539"
{"ok": true, "channel": "github", "action": "read", "backend": "gh", "items": [
  {"title": "CeskaTelevize broken", "author": "jirih", "published_at": "2023-03-14T19:04:52Z",
   "text": "### DO NOT REMOVE OR SKIP THE ISSUE TEMPLATE\n...(issue本文全文)...",
   "raw": {"state": "...", "labels": [...], "comments": 167, "is_pull_request": false}}
]}
```

issue本文はクリーンなMarkdownテキストとして正しく取得できた。**ただし、1点訂正しておきたい
ことがある。** `agent-reach channels`のヘルプ文には`github read`が「Read a repository (with
README) or an issue / PR (with comments)」(コメント付きで読む)と書かれているが、実際に
取得した`items`は1件(issue本文)のみで、`raw.comments`の中身はコメント本文の配列ではなく
**コメント件数を示す整数(167)だけ**だった。つまり、ヘルプの「with comments」という表現は
「コメント数を把握できる」という意味合いであり、コメント本文そのものを一括取得できるわけ
ではなかった(少なくとも検証時点のv1.6.0・`read`アクション単体では)。これは実際に手を
動かして初めて分かった、ヘルプ文言と実際の挙動との小さなギャップである。

それでも、素のcurlでは本文すら読めなかったのに対し、Agent-Reach経由ではissue本文を確実に
読める、という核心的なBefore/After差はクリアに確認できた。

## 5. 唯一クラウドRoutine環境で実行できたこと: PyPIの`agent-reach`は別物(前回PRから再掲)

```
$ pip install agent-reach
$ pip show agent-reach
Name: agent-reach
Version: 0.1.0
Author: Jean Galea
```

`Panniantong/Agent-Reach`の`pyproject.toml`では`authors = [{name = "Neo Reid"}]`で、著者名・
説明文とも完全に異なる。プロジェクト自身の`docs/install.md`が「PyPIのagent-reachはこの
プロジェクトではない」と警告している通りであることを、クラウドRoutine環境で実機確認済み。

## 6. 結論

- クラウドRoutine環境で3つの方法すべてがブロックされていたインストールは、ローカルPCでは
  公式手順通りに一発で成功した。これは実行環境固有の制約であり、Agent-Reach自体の不具合
  ではないことが確定した。
- today.mdの計画通り、GitHub・V2EX・Bilibiliというログイン不要チャンネルは、実際に
  コマンドを叩いて動作を確認できた。YouTube字幕のみ、検証中にYouTube側のレート制限に
  実際に遭遇した(ツールの誤動作ではなく、プラットフォーム側の制限をAgent-Reachが
  正直に伝えている挙動)。
- Before/After比較: GitHubのissueページは素のcurlでは本文すら読めない(クライアントサイド
  レンダリングのため)が、Agent-Reach経由ではissue本文をクリーンなテキストとして確実に
  読める、という核心的な差を実機で確認した。
- 一方、ヘルプ文言の「issue / PR (with comments)」という説明に反し、`github read`が実際に
  返すのはissue本文1件とコメント**件数**のみで、コメント本文そのものの一括取得はできない
  という、ヘルプと実装の小さなギャップも実機で発見した。
- Twitter/Reddit/Xiaohongshu等のログイン前提チャンネルは、today.mdの方針通り今回も検証
  対象外とした(ログイン・ブラウザセッションが必要なため)。
