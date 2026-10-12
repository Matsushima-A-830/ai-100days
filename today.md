# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 015
- 選んだ候補(backlog.mdのタイトルかURL): google/skills — Google公式のAgent Skillsライブラリ(Anthropic版との比較候補) — https://github.com/google/skills
- 補足メモ(あれば):
  - Google Cloud/Gemini関連プロダクト(BigQuery・Cloud Run・GKE・Cloud SQL・AlloyDB・Firebase等)向けのAgent Skillsとプロダクトプラグイン(MCPサーバー連携含む)を集めたGoogle公式リポジトリ(Apache-2.0)。`npx skills add google/skills`でSKILL.md単位にインストールでき、Claude Code/Codex/Antigravity CLI等に対応。
  - **検証結果(results.md)には、day-013で検証したanthropics/knowledge-work-plugins(Anthropic公式Agent Skills)との比較を必須項目として必ず含めること。** 具体的には以下の観点を揃えて比較する:
    - 導入方法の違い: day-013は`claude plugin marketplace add`+`claude plugin install`でプラグイン単位の導入だったのに対し、google/skillsは`npx skills add google/skills`でSKILL.md単位の導入になる。実際のインストールログを両方とも`results.md`に残す。
    - 構成・粒度の違い: day-013(productivityプラグイン)はスキル+スラッシュコマンド+ダッシュボードHTMLのセットだったが、google/skillsは個々のSKILL.mdがどう構成されているか(スラッシュコマンドやMCP連携の有無など)を実際に確認して記録する。
    - ライセンス表記の違い: day-013はApache-2.0で確認済み。google/skillsも同じApache-2.0だが、LICENSEファイルの実在と範囲(プラグイン部分も含むか)を同様の手順で確認する。
    - 可能であれば、day-013で行った「Before/After」形式の検証(ツール利用を禁止した`claude -p`非対話モードで、スキル導入前後の応答がどう変わるかを比較し、`total_cost_usd`・`duration_ms`・`num_turns`等のメタ情報も記録する手法)と同じ測定方法をgoogle/skillsの適切なスキル1つに対しても行い、2社の導入体験・応答品質の変化を横並びで比較できる形にする。
    - 結論として「2社の公式Agent Skills配布のされ方・構成・導入体験の違い」を一言でまとめる節を`results.md`に設ける。
  - 外部クラウドリソース(BigQuery等)に実際に接続するskillを使う場合は別途GCP認証情報が必要になる可能性がある。個々のskill単体の動作確認(ファイル構成の読み込み・応答への反映)には追加の有料APIキーは不要と見込まれるが、検証中に有料API/GCP認証が必須と分かった場合はその旨を正直に記録し、該当skillは見送って別のskillで代替する。
  - 日本語記事は確認した範囲でZenn/Qiita/note共に0件(2026-10-12時点、backlog.md参照)。
  - GPU不要。

状態: 設定済み
