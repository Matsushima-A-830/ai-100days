# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 032
- 選んだ候補(backlog.mdのタイトルかURL): KeygraphHQ/shannon — https://github.com/KeygraphHQ/shannon
- 補足メモ(あれば):
  - 出典: https://github.com/KeygraphHQ/shannon (AGPL-3.0。READMEに「自分が所有する、または明示的な許可を得た環境にのみ実行すること」と明記されている)
  - 概要: Webアプリ/APIのソースコードを解析して攻撃経路を特定し、ブラウザ自動操作とCLIツールで実際に攻撃を再現した上で、動作するPoCが取れた脆弱性のみを報告する自律型AIペネトレーションテストOSS「Shannon Lite」。
  - 検証スコープの指示(厳守):
    1. **検証対象は必ず自分がローカルに立てた、意図的に脆弱なデモアプリ(OWASP Juice Shop等)のみとする。第三者が運用するサイト・サービス・リポジトリには絶対に向けない。** この制約はCLAUDE.mdの方針(認可された検証のみ)に基づくものであり、例外は認めない。
    2. Docker・Node.js 18+を用意し、OWASP Juice Shop(`docker run --rm -p 3000:3000 bkimminich/juice-shop` 等)をローカルに立てる。対象はこのローカルURL(例: `http://localhost:3000`)とそのソースのみ。
    3. `npx @keygraph/shannon@latest setup` でAIプロバイダの認証情報を設定する。既存のAnthropicキーまたはローカルOllama等、追加の有料キー不要の経路を優先する。有料課金が避けられない場合は正直にその旨をresults.mdに記録する。
    4. `npx @keygraph/shannon@latest start -u http://localhost:3000 -r <Juice Shopのローカルrepoパス>` でローカルの脆弱デモアプリに対してのみ実行する。
    5. 実行ログ・検出された脆弱性・PoCの内容(あれば)をそのまま`results.md`に記録する。動かなかった場合・脆弱性が見つからなかった場合も正直に失敗/結果として書く。
    6. README記載では1回のフルスキャンは1〜1.5時間程度。6時間以内に収まらない場合はスコープ(対象エンドポイント数など)を絞る。
    7. GPUは不要。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-29時点、backlog.md参照)。

状態: 設定済み
