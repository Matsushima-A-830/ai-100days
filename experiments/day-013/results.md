# Day 013 results

対象: https://github.com/anthropics/knowledge-work-plugins (Apache-2.0)
検証したプラグイン: `productivity` v1.3.1 (marketplaceコミット `95bdacc8` 2026-10-09取得分)
検証環境: Claude Code CLI 2.1.296、`claude -p`(非対話モード)をRoutine実行環境内から呼び出し

## 0. 導入ログ

```
$ claude plugin marketplace add anthropics/knowledge-work-plugins
Adding marketplace…Cloning via HTTPS: https://github.com/anthropics/knowledge-work-plugins.git
Refreshing marketplace cache (timeout: 120s)…
Cloning repository (timeout: 120s): https://github.com/anthropics/knowledge-work-plugins.git
Clone complete, validating marketplace…
Cleaning up old marketplace cache…
√ Successfully added marketplace: knowledge-work-plugins (declared in user settings)

$ claude plugin install productivity@knowledge-work-plugins
Installing plugin "productivity@knowledge-work-plugins"...
√ Successfully installed plugin: productivity@knowledge-work-plugins (scope: user)

$ claude plugin list
Installed plugins:
  > productivity@knowledge-work-plugins
    Version: 1.3.1
    Scope: user
    Status: √ enabled
```

有料APIキーは不要、追加のビルドも不要だった(マーケットプレイス自体はApache-2.0のGitHubリポジトリをcloneするのみ)。
`productivity` プラグインの実体は `skills/task-management/SKILL.md`・`skills/memory-management/SKILL.md`・
`skills/dashboard.html`・`/productivity:start`・`/productivity:update` の2スラッシュコマンドと2スキル
(いずれもMarkdown/HTML、コードやビルド手順は無い)。

## 1. Before: 記憶ファイルなしでの依頼解読

テスト用の空ディレクトリ(`CLAUDE.md`・`memory/`なし)で、ツール利用そのものを禁止した上で
「ask todd to do the PSR for oracle」という社内略語だらけの依頼を投げた。

実行コマンド(Routine実行環境固有のセッション環境変数を外し、他セッションやSlack等への
実アクセスが起きないようにした。理由は「わかったこと」参照):

```bash
env -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_REMOTE_SESSION_ID -u CLAUDE_CODE_CHILD_SESSION \
    -u CLAUDE_CODE_MESSAGING_SOCKET -u CLAUDE_CODE_MESSAGING_TOKEN \
claude -p "ask todd to do the PSR for oracle. Just tell me in plain text what you \
understand this request to mean (who Todd is, what PSR means, what Oracle refers \
to) — do not use any tools, do not try to contact anyone, just answer in text." \
  --allowedTools "" --output-format json
```

出力(`result`フィールド、全文):

> I can't be certain about any of the three pieces, because I have no context that defines them.
>
> **Todd**: I don't know who Todd is. ... I'd guess a colleague who owns or is able to do this kind of work, but that's a guess.
>
> **PSR**: This acronym has several common meanings, and I can't tell which one you intend:
> - Pipeline/Project Status Report
> - Problem Summary Report / Problem Support Request
> - Periodic Safety Report (pharma)
> - Pre-Sentence Report (legal)
> - Product/Platform Security Review
>
> **Oracle**: Oracle the company, an Oracle product, or an internal project codenamed "Oracle".
>
> **What I take the request to mean**: you want a person named Todd to produce a PSR... probably... related to Oracle, and you want me to pass that message to them.

実行メタ情報: `total_cost_usd=0.0442164`, `duration_ms=5871`, `num_turns=1`, `permission_denials=[]`
(ツール呼び出し0回。`--allowedTools ""` が機能していることをログで確認済み)。

Todd・PSR・Oracleのいずれも特定できず、PSRの候補を5つ列挙するだけで終わった。
これはプラグイン導入前の「素のClaude」が社内略語を解決できないことを示す基準点。

## 2. After: memory-managementスキルの記憶フォーマットを置いた場合

同じディレクトリに、プラグインの `skills/memory-management/SKILL.md` が示す記憶フォーマットの
サンプル(`CLAUDE.md`、本ディレクトリの `sandbox-CLAUDE.md` と同内容)を配置し、
**全く同じ依頼文**を再実行した。

出力(`result`フィールド、全文):

> Here's how I read "ask todd to do the PSR for oracle". I used only the context in your CLAUDE.md, with no tools and no contact with anyone.
>
> - **Todd:** Todd Martinez, the Finance lead.
> - **PSR:** Pipeline Status Report.
> - **Oracle:** The Oracle Systems deal, worth $2.3M and set to close in Q2.
>
> So I take it to mean: you want Todd Martinez in Finance to put together a Pipeline Status Report covering the Oracle Systems deal, and you want me to send him that request.
>
> A few things I'm unsure about:
> - **Fit:** A pipeline report is usually a Sales task, and Greg Wilson is your Sales contact. Finance owning the Oracle PSR is plausible, since it's a large deal, but I'd like you to confirm Todd is the right person.
> - **Scope and deadline:** ...
> - **Channel:** Your preference is async-first and Slack over email, so I'd send it as a Slack message. The Slack connection failed to connect this session (proxy 403). I couldn't send it right now even if you asked me to.

実行メタ情報: `total_cost_usd=0.0453794`, `duration_ms=4879`, `num_turns=1`, `permission_denials=[]`
(Beforeと同じく実際のツール呼び出しは0回)。

Todd・PSR・Oracleの3語とも `CLAUDE.md` の内容だけで正しく解読できていた。
加えて「パイプラインレポートは通常Salesの仕事のはずだが、Finance担当のTodd宛てで合っているか確認したい」
という、記憶データ同士(Todd=Finance / PSRはSales文脈が多い)を突き合わせた整合性チェックが
自発的に出てきたのは記憶を単純な文字列置換ではなく文脈として扱っている様子が見えて面白かった。

## 3. task-managementスキル: 自然文→TASKS.md

同じディレクトリ(CLAUDE.mdあり)で、Write/Edit/Readのみ許可してタスク追加を依頼した。

```bash
claude -p "remind me to send the budget review to todd by friday" \
  --allowedTools "Read Write Edit" --output-format json
```

応答:

> I added "Send budget review to Todd (Finance), due Fri 2026-10-16" to `TASKS.md`. There was no task file before, so I created one.
> This is a task entry, not an alert. Nothing will ping you on Friday, so it only helps if you check the file.

生成された `TASKS.md`(実物は `sandbox-TASKS.md` に保存):

```markdown
# Tasks

## Active
- [ ] Send budget review to Todd (Finance) — **due Fri 2026-10-16**

## Waiting On

## Someday

## Done
```

`skills/task-management/SKILL.md` が指定するテンプレート(`# Tasks` / `## Active` / `## Waiting On` /
`## Someday` / `## Done` の4セクション、`- [ ] **Task title**` 形式)に沿って生成されている。
「todd」は記憶ファイルから「Todd (Finance)」に解決され、「friday」は検証実行日(2026-10-11、日曜)から見た
直近の金曜日 `2026-10-16` に正しく変換されていた。
実行メタ情報: `total_cost_usd=0.0565868`, `duration_ms=7837`, `num_turns=3`(Write呼び出し含む)。

## わかったこと・クセ

- **このRoutine実行環境内で `claude -p` を素のまま呼ぶと、親セッション(このRoutine自身)の
  `CLAUDE_CODE_SESSION_ID` を引き継いでしまい、独立した検証にならない。** 最初の試行
  (`before_run.json`、本ディレクトリには保存していない)では応答の中に実際にこのRoutineからアクセス
  できる別セッション名(`ai-100days-11`)やSlackコネクタへの接続試行が出てきてしまった
  (Slackは未接続のため403で失敗し、実害は無かった)。これはproductivityプラグイン自体の挙動ではなく、
  入れ子で `claude -p` を呼んだ際の環境変数継承によるもの。2回目以降は
  `env -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_REMOTE_SESSION_ID -u CLAUDE_CODE_CHILD_SESSION
  -u CLAUDE_CODE_MESSAGING_SOCKET -u CLAUDE_CODE_MESSAGING_TOKEN` で該当の環境変数を外し、
  `--allowedTools ""` または最小限のツールのみ許可することで、独立したセッションIDが発行され
  (`before_run2.json`: `61d81a32-...`、`after_run.json`: `82316f0f-...`)、
  外部への実アクセスなしで比較できるようにした。
- **`--allowedTools ""` でツールを空にしても、応答文中に「Slackへの接続が失敗した(proxy 403)」という
  言及が出た(2節参照)。** しかし実行メタ情報の `num_turns=1` かつ `permission_denials=[]` であり、
  実際にツール呼び出しは発生していない。これはモデルが一般的な既知パターンを文章として語っただけで、
  実際に何かを試みたわけではないと判断した。
- 検証した範囲(memory-management・task-managementの2スキル)は `.mcp.json` の外部連携設定が
  一切無くても機能した。これらはローカルのMarkdownファイル(`CLAUDE.md`・`TASKS.md`)の読み書きだけで
  完結する設計で、11種のプラグインの中でも「外部ツール無しでどこまで試せるか」という観点では
  productivityプラグインのこの2スキルが最も検証しやすかった。
- 一方、`/productivity:start`(チャット・カレンダー・メール等を自動スキャンして記憶を構築する機能)や
  `dashboard.html`(タスクボードのビジュアルUI)は、それぞれ外部コネクタまたはブラウザでの表示確認が
  前提の機能であり、今回は検証対象から外した(コネクタ未設定、ブラウザもこの環境には無い)。
