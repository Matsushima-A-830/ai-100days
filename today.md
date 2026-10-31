# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 034
- 選んだ候補(backlog.mdのタイトルかURL): pbakaus/impeccable — https://github.com/pbakaus/impeccable
- 補足メモ(あれば):
  - 出典: https://github.com/pbakaus/impeccable (Apache-2.0。元Google Developer Advocate・jQuery UI作者のPaul Bakaus氏。Anthropic公式の`frontend-design`スキルを土台に拡張)
  - 概要: AIコーディングエージェントが生成するUIの「いかにもAI感」を防ぐための、LLM・APIキー不要の62個の決定的ルールベース検出器+エージェント向けコマンド群(polish/critique/audit等)。`npx impeccable detect`でソースディレクトリやURLをスキャンし、詰まったパディングや見出しレベルのスキップ等の「AIっぽい」デザインパターンをJSON出力・GitHub Actionsアノテーションで報告する。ライブモードではdevサーバー上でUI要素のバリアント比較・適用もできる。
  - 検証スコープ・手順:
    1. Node.js環境を用意し、`npx impeccable detect`を本リポジトリの`posts/cards/`以下にある既存のシェアカードHTML(過去のday-NNN.html、または土台である`tools/card-template.html`)に対して実行する。
    2. 検出された指摘項目(ルールID・該当箇所・指摘内容)をそのまま`results.md`に記録する。失敗した場合(検出器が動かない等)も正直に書く。
    3. 指摘の中から実際に手を動かして直せるものを1〜2件選んで修正し、再度`impeccable detect`を実行して指摘が解消されたことを確認する(Before/After比較)。ただし`tools/card-template.html`自体は編集しない(CLAUDE.md記載のとおり、シェアカードの骨格は100日シリーズ共通テンプレートのため直接編集禁止)。修正を当てる場合は`experiments/day-034/`配下に複製したファイルに対して行う。
    4. 可能であれば`critique`等のエージェント向けコマンドやライブモード(devサーバー上でのバリアント比較)も触ってみて、その様子もresults.mdに記録する。
    5. GPU不要・追加の有料APIキー不要。`npx`によるパッケージ取得・軽いテレメトリ通信がRoutine実行環境のネットワーク制限で問題なく行えるか確認し、行えない場合は「Routine環境の制約」として記事に書かずresults.mdに1〜2行だけ残してローカル検証にエスカレーションする。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-31時点、backlog.md参照)。
  - 記事化の切り口: 本リポジトリ自前のシェアカードHTML(`posts/cards/day-NNN.html`)を実際に`impeccable detect`でスキャンし、指摘された項目と直した結果をBefore/Afterで見せる自己言及的な検証にする。

状態: 設定済み
