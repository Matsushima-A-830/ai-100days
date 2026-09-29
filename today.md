# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 002
- 選んだ候補(backlog.mdのタイトルかURL): Google、GeminiでgiflibをAI支援でRustに書き換え差分ファジングで検証(企業ブログ) — https://bughunters.google.com/blog/scaling-memory-safety (解説記事: https://www.infoq.com/news/2026/09/c-rust-rewrite/)
- 補足メモ(あれば): Googleの元事例はgiflib全体(約3,000行)をAI支援でRustに書き換え、ABI互換のドロップイン実装として差分ファジングで検証したというもの。
  6時間以内に一人で再現するのはフルスコープでは非現実的なため、スコープを縮小し、小規模なC言語コード片(数十〜数百行程度、メモリ安全上の欠陥を意図的に含むもの)を選び、
  Claude Code自身の機能だけでRustへの書き換えを行い、単体テスト・fuzzing的な入力比較でC版とRust版の挙動差分を検証する、というミニ実験にする。
  外部APIキー・GPUは不要。ライセンス・出典明記を忘れないこと。

状態: 設定済み
