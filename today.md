# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 030
- 選んだ候補(backlog.mdのタイトルかURL): heygen-com/hyperframes — https://github.com/heygen-com/hyperframes
- 補足メモ(あれば):
  - 出典: https://github.com/heygen-com/hyperframes (HeyGen社が2026年4月にOSS公開、本日GitHub Trending TypeScriptで言及)
  - 概要: HTML/CSS/GSAPアニメーションをヘッドレスChrome+FFmpegで確定的にMP4動画へレンダリングするOSS(Apache-2.0)。コア機能は外部APIキー不要。Qiitaに導入記事1件あるが独自検証記事は未検出。
  - 検証スコープの指示:
    1. 自作のHTML/CSS/GSAPアニメーションを1つ以上用意し、`npx hyperframes init`等で導入してMP4へレンダリングする。
    2. 同じ入力から複数回レンダリングして出力が確定的(毎回同じ)であることを確認する。
    3. 本リポジトリのX投稿用シェアカード(`posts/cards/day-NNN.html`)をベースに、静止画カードと動画版のBefore/After比較ができると見栄えが良い。
    4. HeyGen社の生成AIメディア連携(オプション機能)は有料APIキーが必要な可能性があるため、今回はコアのHTML→MP4レンダリング機能のみを検証対象とする。
    5. Routine実行環境にヘッドレスブラウザ(Chromium)が無く動作しない場合は、CLAUDE.mdの「Routine環境の制約」エスカレーションルールに従い、PR本文冒頭に「ローカル検証が必要」と明記し再現手順を添える。
  - 日本語記事件数: Zenn 0件 / Qiita 1件 / note 0件(2026-10-27時点、backlog.md参照)。

状態: 設定済み
