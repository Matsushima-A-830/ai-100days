# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 053
- 選んだ候補(backlog.mdのタイトルかURL): awslabs/cli-agent-orchestrator — https://github.com/awslabs/cli-agent-orchestrator
- 補足メモ(あれば):
  - 出典: https://github.com/awslabs/cli-agent-orchestrator (Apache-2.0。2026-11-19付研究PR〈#181〉でbacklog.mdに追記。AWS Open Source Blog発表記事: https://aws.amazon.com/blogs/opensource/introducing-cli-agent-orchestrator-transforming-developer-cli-tools-into-a-multi-agent-powerhouse)
  - 概要: AWS Labsが公開した、Claude Code・Codex CLI・Kiro CLI・GitHub Copilot CLI・Cursor CLI等、既に認証済みのAIコーディングCLIをプロバイダーとして束ね、supervisorエージェントが各CLIを独立したtmuxセッションで並列・直列に動かしてタスクを分担させるオーケストレーションフレームワーク。各エージェントは自身のネイティブな認証・機能を保ったまま、完全なCLIプロセスとして起動される。
  - 選定理由: Apache-2.0。追加の有料APIキー・GPU不要で、導入済みのClaude Code CLI自身をプロバイダーとして使える。本チャレンジ自体がClaude Code Routineで運用されているため、「Claude Code自身をsupervisor配下のサブエージェントとして動かす」という自己言及的な検証ができる点を評価した。
  - APIキー・前提条件についての方針: 追加の有料APIキーは不要(導入済みのClaude Code CLI自身をプロバイダーとして使う)。GPU不要。Python 3.11+・tmux 3.3+・uvの導入が前提。
  - 検証スコープ・手順(案):
    1. `uv`でcli-agent-orchestratorを導入し、導入ログをそのまま記録する。
    2. `cao install code_supervisor`→`cao-server`→`cao launch`で、Claude Code CLIをプロバイダーとしたsupervisor構成を立ち上げる。
    3. supervisorに複数のサブタスク(例: 複数ファイルへの軽い修正・調査タスクの分担)を与え、tmux上で各サブエージェントが並列・直列に動く様子を記録する(ログ・可能ならスクリーンショット)。
    4. 動かなかった場合も失敗として正直に`results.md`に記録する。tmux非対応等、Routine実行環境固有の制約で進まない部分はローカル検証にエスカレーションする。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-19時点、backlog.md参照。検索範囲では日本語での一次検証記事は未検出)。
  - 記事化の切り口: 本チャレンジを運用しているClaude Code自身をsupervisor配下のサブエージェントとして動かし、複数タスクを並列処理させる様子を見せる自己言及的な構成。tmuxの分割画面はスクリーンショット映えする。

状態: 設定済み
