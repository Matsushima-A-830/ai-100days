# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 035
- 選んだ候補(backlog.mdのタイトルかURL): Claude Code Game Studios — https://github.com/Donchitos/Claude-Code-Game-Studios
- 補足メモ(あれば):
  - 出典: https://github.com/Donchitos/Claude-Code-Game-Studios (MIT。本日GitHub Trending Shellで言及)
  - 概要: Claude Codeの1セッションを、Director/部門リーダー/専門職の3階層・49体のエージェント、74個のスラッシュコマンド形式スキル、15個のフック(自動検証)、14個のパス限定ルール、62個のドキュメントテンプレートからなる「ゲーム開発スタジオ」として動かすMITライセンスのテンプレート。Godot 4/Unity/Unreal Engine 5に対応し、`/start`で状況を聞かれてワークフローに誘導される。README自身が「パースチェックは実行確認ではない」「画面の変化を伴う修正は、実際にゲームを起動しスクリーンショットを`production/qa/evidence/`に残すまで完了としない」と強く検証を要求している点が特徴。追加APIキー・GPU不要(Claude Code自体の認証のみ)。
  - 検証スコープ・手順:
    1. リポジトリをクローンし、`experiments/day-035/`配下にテンプレートを展開してプロジェクトルートでClaude Codeを起動する(サブフォルダから起動するとhooks・denyルール・ask-firstパーミッションがスキップされる旨がREADMEに明記されているため注意)。
    2. `/start`を実行し、どのような質問・ワークフロー誘導をされるかをそのままresults.mdに記録する。
    3. 全49エージェント・74スキルを使ったフルのゲーム開発サイクルは6時間に収まらないため、スコープを絞る: `/setup-engine godot 4.7`等でエンジンをセットアップし、`/brainstorm`のような企画系スキルを1〜2個実行して、どのエージェントが呼ばれ、どんな出力(ドキュメント・コード等)が生成されるかを記録する。
    4. `/skill-test static`または`/skill-test audit`を実行し、スキル/エージェント構成の構造チェック結果(カバレッジ等)をresults.mdに記録する。
    5. 可能であれば小さな1画面程度のプロトタイプを実際に生成させ、README自身の検証ルールに従って実際にゲームを起動・動作確認し、スクリーンショットを`production/qa/evidence/`相当の場所に残す。
    6. 実行コマンド・ログ・エラーはすべてそのままresults.mdに記録する(失敗した場合も正直に書く)。`npx`/Claude Code自体のネットワーク通信がRoutine実行環境の制約で行えない場合は「Routine環境の制約」として記事には書かず、results.mdに1〜2行だけ残してローカル検証にエスカレーションする。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-01時点、backlog.md参照)。
  - 記事化の切り口: 本リポジトリ自体がClaude Code Routineで運用されているという自己言及的な文脈に合わせ、49エージェント・74スキルという大規模な構成を実際に動かしたログ・生成物・スクリーンショットをそのまま見せる。

状態: 設定済み
