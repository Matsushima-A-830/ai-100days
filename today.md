# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 013
- 選んだ候補(backlog.mdのタイトルかURL): anthropics/knowledge-work-plugins — Anthropic公式、Claude Cowork/Code向け職種別プラグイン集 — https://github.com/anthropics/knowledge-work-plugins
- 補足メモ(あれば):
  - Apache-2.0ライセンス。Anthropic自身が公開した、Claude Cowork(および Claude Code)向けの職種特化プラグイン集。productivity/sales/customer-support/product-management/marketing/legal/finance/data/enterprise-search/bio-research/cowork-plugin-managementの11種を収録。各プラグインはskills・MCP連携(`.mcp.json`)・slashコマンド・サブエージェントをMarkdown/JSONのみで構成しており、コード・ビルドは不要。
  - 導入は`claude plugin marketplace add anthropics/knowledge-work-plugins`→`claude plugin install <plugin>@knowledge-work-plugins`。追加の有料APIキー不要、GPUも不要。外部ツール(Slack/Notion/HubSpot等)と連携するMCPは`.mcp.json`経由だが、未設定でも各skill・slashコマンド単体の動作検証は可能(そちらに絞って検証する)。
  - 検証の軸: productivityプラグイン(または外部連携が要らない別プラグイン)を実際に導入し、`/productivity:...`等のslashコマンドやskillの自動発火を試す。導入前後で同じ職務特化タスク(議事録整理・スプレッドシート作成・要件のまとめ等)への応答がどう変わるかをBefore/Afterで比較する。
  - 日本語記事は確認した範囲でZenn/Qiita/note共に0件(2026-10-10時点、backlog.md参照)。Anthropic公式発というニュース価値も高い。

状態: 設定済み
