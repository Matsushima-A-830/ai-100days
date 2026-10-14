# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 017
- 選んだ候補(backlog.mdのタイトルかURL): K-Dense-AI/scientific-agent-skills — AIエージェントを「AI研究者」に変えるAgent Skills集(旧Claude Scientific Skills) — https://github.com/K-Dense-AI/scientific-agent-skills
- 補足メモ(あれば):
  - 生物学・化学・医学・物理・工学・地球科学・データ解析・科学コミュニケーションにまたがる163種のスキルと、100種類超の科学データベースへのガイダンスを収録したAgent Skills集(MIT。個々のスキルのライセンスは`SKILL.md`ごとに異なる場合があるため、実際に使うスキルのライセンス表記も確認すること)。元はClaude Scientific Skillsという名前だったが、Claude専用ではなく汎用のオープンなAgent Skills標準に対応するホスト(Claude Code/Cursor/Codex/Google Antigravity等)向けに改称された。
  - 導入は `npx skills add K-Dense-AI/scientific-agent-skills`。
  - **検証の軸は「APIキー不要なスキルに絞って、Claude Code自身にスキル無し/有りで同じ疑似研究タスクを解かせ、応答の深さ・正確さがどう変わるかを比較する」こと。** 具体的には以下を`results.md`に残す:
    - リポジトリ内のスキル一覧(`SKILL.md`)を確認し、外部APIキー(Exa・Benchling・NCBI・Materials Project等)が不要なスキルを2〜3個選ぶ(候補: 統計解析・文献レビュー手法・データ可視化系など、具体的にどれを選んだか理由とともに明記)。
    - 選んだスキルを実際に `npx skills add` で導入し、導入ログ(成功/失敗・出力)をそのまま記録する。
    - スキル無しの状態と、スキル導入後の状態で、同一の簡単な疑似研究タスク(例: 「ある小規模な実験データセットを渡して統計的に妥当な検定手法を選ばせ理由を説明させる」等、具体的に設計すること)をClaude Codeに解かせ、両者の回答を並べてBefore/After比較する。
    - GPU不要・APIキー不要の範囲に検証スコープを限定したことと、その理由(CLAUDE.mdの「当面は有料APIキーが必須の候補を選ばない」方針)を`results.md`冒頭に明記する。
    - ライセンス表記(リポジトリ全体のMIT、および実際に使ったスキルの`SKILL.md`内のライセンス記載)を確認する。
  - 日本語記事は確認した範囲でZenn/Qiita/note共に0件(2026-10-14時点、backlog.md参照)。英語のDEV Community記事等はあるが日本語の一次検証記事ではない。
  - GPU不要。スキルによってはExa・Benchling・NCBI・Materials Project等の有料/要登録APIキーが必要だが、今回の検証スコープではそれらを使わない。

状態: 設定済み
