# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 023
- 選んだ候補(backlog.mdのタイトルかURL): Graphify-Labs/graphify — https://github.com/Graphify-Labs/graphify
- 補足メモ(あれば):
  - 人間(matsu)から直接指定された候補(research: 2026-10-20分のネタ候補PR〈#79、backlog.md追記、マージ待ち〉内の候補の1つ)。
  - 出典: https://github.com/Graphify-Labs/graphify (2026-10-20時点GitHub Trending Pythonで+906star/日、累計約130k star)。開発者Safi Shamsi名義の個人リポジトリ〈safishamsi/graphify〉から移管/ミラーされた可能性があり記事によってURL表記が揺れているため、検証時はGraphify-Labs/graphifyが現行の公式であることを確認すること。
  - 概要: コード・ドキュメント・SQLスキーマ・設定ファイル・PDF・画像・動画を1つのクエリ可能なナレッジグラフに変換するPython CLI兼Claude Code/Cursor/Codex/Gemini CLI向けスキル。コード解析はtree-sitterによる完全ローカル・LLM不要の決定的処理で、`--code-only`を使えば外部送信なしの完全オフライン動作が可能(ベクトルストア不使用)。出力は操作可能な`graph.html`・`GRAPH_REPORT.md`・`graph.json`で、grepやReadの繰り返しの代わりに`graphify query`等でグラフに問い合わせる運用を想定。
  - 検証範囲: `uv tool install graphifyy`で導入し、`graphify install`でClaude Code等にスキルを登録する。本リポジトリ(ai-100days)自身のコードベース(experiments/配下のPythonコード等)に対して`--code-only`で`/graphify`を実行し、生成された`graph.html`/`GRAPH_REPORT.md`を確認する。その上で、同じ調査タスク(例:「day-0XXの実験で使われているライブラリと関数呼び出し関係を調べる」等)を、(a)従来のgrep/Read中心の探索と、(b)graphifyのグラフへの問い合わせ、の両方で実行し、ターン数・読み込んだトークン量(概算)・所要時間をBefore/After比較する。公式が主張するトークン削減率(日本語記事で言及されている「71.5分の1」等)が自分の環境・自分のコードベース規模でどの程度再現するかを実測する。
  - 追加の有料APIキーは不要(`--code-only`モードはLLM呼び出しなしの完全ローカル処理)。GPUも不要。
  - 日本語記事件数: Zenn 2件以上 / Qiita 1件以上 / note 5件以上(2026-10-20時点、backlog.md参照。公式主張のトークン削減率を疑問視する検証記事も既にある)。既に日本語記事が多いため、差別化として「本チャレンジ自身(ai-100days)のリポジトリという具体的な中規模Pythonコードベースでの実測」に焦点を絞ること。
  - 記事化の切り口: 「AIコーディングエージェントのgrep/Read探索を、ナレッジグラフへの問い合わせに置き換えたら、本当にトークンは減るのか」を自分のリポジトリで実測するBefore/After比較。ライセンス表記(Apache-2.0/MIT両方の記載あり)を確認し記事に明記する。グラフ生成がLLM不要・完全ローカルで完結する点(プライバシー面のメリット)にも触れる。

状態: 設定済み
