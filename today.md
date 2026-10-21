# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 024
- 選んだ候補(backlog.mdのタイトルかURL): DietrichGebert/ponytail — https://github.com/DietrichGebert/ponytail
- 補足メモ(あれば):
  - 人間(matsu)から直接指定された候補(research: 2026-10-21分のネタ候補PR〈#82、backlog.md追記〉内の候補の1つ)。
  - 出典: https://github.com/DietrichGebert/ponytail (2026-10-21時点GitHub Trending 全言語で+2,051star/日)
  - 概要: コーディングエージェントを「最も怠惰なシニア開発者」のように振る舞わせ、新しいコードを書く前に既存コード・標準ライブラリ・プラットフォーム標準機能の再利用を優先させ、リスクの高いロジックにはテストを残しつつ不要な抽象化や冗長なコードを削るルールセット(MITライセンス)。Claude Code/Codexへのプラグイン導入や、他エージェント向けのAGENTS.md/SKILL.md配置に対応し、`/ponytail-review`・`/ponytail-audit`等のレビュー・監査コマンドも備える。
  - 検証範囲: `/plugin marketplace add DietrichGebert/ponytail` → `/plugin install ponytail@ponytail` でClaude Codeに導入する。同程度の複雑さを持つ同じコーディングタスクを、(a)ponytail導入前のClaude Codeと、(b)ponytail導入後のClaude Code、の両方に与え、生成コード行数・トークン使用量(概算)・応答時間・テストの有無をBefore/After比較する。公式が主張する「54〜94%のコード削減」等の数値が自分の環境・自分のタスクでどの程度再現するかを実測する。`/ponytail-audit`で本リポジトリの既存コード(experiments/配下等)を監査し、指摘内容も確認する。
  - 追加の有料APIキーは不要(Claude Code自身のサブスクリプション認証のみで検証可能)。GPUも不要。Node.jsがPATH上にあれば動作。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-21時点、backlog.md参照。zenn.dev/qiita.com/note.comへのsite:検索ではいずれも0件。海外の日本語訳記事が1件あるのみ)。日本語での一次検証記事が無いため差別化はしやすいが、公式主張の数値(独立検証では小さく出るとの報告あり)を自分の環境で実測する点を記事の主眼にすること。
  - 記事化の切り口: 「コーディングエージェントに"怠惰なシニア開発者"を演じさせたら、本当にコードは減るのか」を自分の環境・自分のタスクで実測するBefore/After比較。公式ベンチマークの数値と自分の実測値のギャップがあれば正直に書く。本リポジトリで既に扱ったandrej-karpathy-skills(CLAUDE.mdでの原則提示のみ)との違い(実装・計測コマンドまで備える点)にも触れる。

状態: 設定済み
