# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 019
- 選んだ候補(backlog.mdのタイトルかURL): xerj-org/xerj — AIエージェント専用のローカル検索エンジン(Elasticsearch API互換、Rust製) — https://github.com/xerj-org/xerj
- 補足メモ(あれば):
  - 人間(matsu)から直接指定された候補で、通常の「朝research→通勤中にtoday.md反映→昼実装」という分業を経ず、同日中に選定から検証まで一括で実施した。
  - コード・ドキュメント・ログ・PDF等のフォルダをまるごとインデックス化し、AIエージェントがファイル全体を読み込まずに該当箇所だけを取り出せるようにするローカル検索エンジン(Apache-2.0)。全文検索(BM25)・ベクトル検索・ハイブリッド検索に対応し、Elasticsearch 8.x互換APIとMCPサーバー(16ツール)を備える単一バイナリ。
  - 導入はGitHub Releasesの公式プリビルドバイナリ(`x86_64-unknown-linux-gnu`)をダウンロードするのみ。追加の有料APIキー不要。既定(lexical)モードはGPU不要、`--embed-mode neural`はCPUでも動くが低速。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-16時点、backlog.md参照)。
  - 検証は本リポジトリ(ai-100days)自身をautoindexの対象にして行った。

状態: 設定済み
