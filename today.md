# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 012
- 選んだ候補(backlog.mdのタイトルかURL): video-shotcraft — Claude Code/Codex向けの「映画的プロダクト動画」自動生成agent skill(Remotion土台) — https://github.com/Vincentwei1021/video-shotcraft
- 補足メモ(あれば):
  - Apache-2.0ライセンス。Claude Code/Codex向けのagent skillとしてリポジトリをクローンしskillsディレクトリにシンボリックリンクするだけで導入可能。追加の有料APIキーは不要、GPUも不要(Remotion自体は個人・小規模チーム利用は無料だが企業利用は別途ライセンス契約が必要な場合がある点に注意)。
  - 152枚のショットレシピカード・209本のモーションプレビュー・すぐ使える36.2秒のプロモ用テンプレート「Ink Press」が付属。まずはこのテンプレートをレンダリングし、実際に生成された短いプロモ動画そのものをデモにする。
  - ヘッドレスLinux環境でのレンダリングには`--concurrency=1`指定・ヘッドレスChromeの差し替え(chrome-headless-shellへ)・`--browser-executable`指定が必要と報告されている。day-009(OpenMontage)でRemotionのheadlessレンダリングに詰まった経験があるので、その知見が活かせるか/今回は同じ詰まり方をするかを比較軸にすると良い。
  - 検証の軸は「自然言語の指示だけでどこまで映画的なプロダクト動画が組み立てられるか」と「day-009で遭遇したRemotionのレンダリング詰まりどころが、スキル化によってどれだけ解消されているか」の2点。
  - 日本語記事は確認した範囲でZenn/Qiita/note共に0件(2026-10-09時点、backlog.md参照)。中国語記事・英語ブログでの紹介はある。

状態: 設定済み
