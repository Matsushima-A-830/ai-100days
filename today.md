# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 059
- 選んだ候補(backlog.mdのタイトルかURL): colbymchenry/codegraph — コーディングエージェント向けのローカルコード知識グラフ — https://github.com/colbymchenry/codegraph
- 補足メモ(あれば):
  - 出典: https://github.com/colbymchenry/codegraph (MIT。本日GitHub Trending TypeScriptで+99star/日)
  - 概要: ローカルのSQLiteに関数・クラス等のシンボルと呼び出し/参照関係をグラフとして事前インデックスし、MCP経由でClaude Code・Cursor・Codex等のコーディングエージェントに公開するツール。エージェントがgrep/Readを繰り返す代わりに1回のクエリで関連コードを取得できるとして、トークン数・ツール呼び出し数の削減を謳う。
  - 日本語記事件数: Zenn 0件 / Qiita 1件(自社リポジトリで試した際、コールグラフで検出できたのは対象4箇所中2箇所のみだったという実利用レポート) / note 0件
  - APIキー・前提条件についての方針: 追加の有料APIキー不要、GPU不要、完全ローカル。`npx @colbymchenry/codegraph`→`codegraph init`で導入できる。
  - 検証スコープ・手順(案):
    1. `npx @colbymchenry/codegraph`の導入ログを記録する。
    2. 本リポジトリ(ai-100days)自身か、`experiments/`配下の既存コードを対象に`codegraph init`を実行し、インデックス構築にかかった時間・生成されたグラフの規模を記録する。
    3. 実際に関数呼び出し関係のクエリを試し、正しく関連コードを返すかを確認する。
    4. Qiita記事(実利用レポート)が指摘する「同じ判定を独立に再実装した重複コードは呼び出し関係が無く検出できない」という限界が、自前の検証コードでも再現するかを試す。
    5. 導入前後(grep/Readの繰り返し vs 1回のクエリ)でのツール呼び出し回数・やり取りの簡潔さを比較できる形で`results.md`に記録する。失敗した場合も失敗として正直に書く。
  - 記事化の切り口: 「grepを繰り返す代わりに1回のクエリで関連コードを返す」という主張を、自分のコードベースで実際に検証し、Qiita記事が報告する検出漏れが再現するかどうかも含めて技術的に見せる。
  - 注記: backlog.mdでは一旦p-e-w/heretic(abliteration)がDay-059として採用されていたが、人間の判断でcolbymchenry/codegraphに差し替えた。heretic側のbacklog.mdエントリは「未選択」に戻し、codegraph側を「採用済み(day-059)」に更新済み。

状態: 設定済み
