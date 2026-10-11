# Day 013: anthropics/knowledge-work-plugins の productivity プラグインを導入し、記憶(メモリ)機能のBefore/Afterを検証する

対象: https://github.com/anthropics/knowledge-work-plugins (Apache-2.0)、`productivity` プラグイン v1.3.1
検証時点のマーケットプレイスの最新コミット: `95bdacc803aa5cfdb10f35e5b9fb2d4b11100133` (2026-10-09)

詳しい経緯・実測値・判明したクセは `results.md` を参照。ここでは再現手順のみをまとめる。

## 再現手順

### 1. マーケットプレイス追加とプラグイン導入

```bash
claude plugin marketplace add anthropics/knowledge-work-plugins
claude plugin install productivity@knowledge-work-plugins
claude plugin list   # Status: enabled になっていることを確認
```

### 2. Before: 記憶ファイルが無い状態で略語入りの依頼を投げる

空のディレクトリで、ツール利用・外部連絡を禁止した上で同じ依頼を投げる。

```bash
mkdir sandbox && cd sandbox
claude -p "ask todd to do the PSR for oracle. Just tell me in plain text what you \
understand this request to mean (who Todd is, what PSR means, what Oracle refers \
to) — do not use any tools, do not try to contact anyone, just answer in text." \
  --allowedTools "" --output-format json
```

→ Todd・PSR・Oracleのどれも特定できず、可能性を列挙するだけの回答になる(`results.md` 1節)。

### 3. After: productivityプラグインのmemory-managementスキル形式でCLAUDE.mdを置く

`sandbox/CLAUDE.md` として本ディレクトリの `sandbox-CLAUDE.md` をコピーする
(内容はプラグインの `skills/memory-management/SKILL.md` に載っている記憶フォーマットの例をそのまま使用)。

```bash
cp ../sandbox-CLAUDE.md CLAUDE.md
claude -p "(同じ依頼文)" --allowedTools "" --output-format json
```

→ Todd=Todd Martinez(Finance)、PSR=Pipeline Status Report、Oracle=Oracle Systemsディール($2.3M)
と正しく解読し、さらに「パイプラインレポートは通常Salesの仕事では?」という整合性チェックまで加えた
回答になる(`results.md` 2節)。

### 4. task-managementスキル: 自然文からTASKS.mdへの変換

```bash
claude -p "remind me to send the budget review to todd by friday" \
  --allowedTools "Read Write Edit" --output-format json
cat TASKS.md
```

→ `skills/task-management/SKILL.md` が指定するテンプレート通りに `TASKS.md` が新規作成され、
CLAUDE.mdのメモリで「todd」を「Todd (Finance)」に解決し、「friday」を実際の日付
(検証実行日2026-10-11から見た直近金曜 `2026-10-16`)に変換したタスクが1件追加される
(`results.md` 3節、実物は `sandbox-TASKS.md`)。

## 注意

- 3回のテスト実行はいずれも `CLAUDE_CODE_SESSION_ID` 等のRoutine実行環境固有の環境変数を
  `env -u` で外し、`--allowedTools` でツールを最小限(または空)に絞った、独立した `claude -p` 呼び出しである。
  外した理由は `results.md` の「わかったこと」を参照。
- 本検証はプラグインの外部連携(Slack/Notion/HubSpot等のMCP)を一切使わず、
  `.mcp.json` 設定なしでも動く範囲(メモリ解読・タスク管理)に絞っている。
