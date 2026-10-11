---
title: "Anthropic公式の職種特化プラグイン集「knowledge-work-plugins」のメモリ機能で社内略語を解読させてみた"
emoji: "🗂️"
type: "tech"
topics: ["ai", "claudecode", "oss", "productivity", "llm"]
published: false
---

筆者は海外のAI関連ニュースを毎日1本検証して発信するチャレンジの13日目として、Anthropic自身が公開した[knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)を実際にインストールして動かしてみた。Claude Cowork/Claude Code向けの職種特化プラグイン集(Apache-2.0)で、productivity/sales/legal/finance/dataなど11種類が収録されている。各プラグインはコードではなくMarkdown/JSONのskill定義とMCP連携設定のみで構成されており、ビルドは不要だった。筆者が検索した範囲ではZenn・Qiita・noteのいずれにも日本語での一次紹介記事は見つからなかった(2026-10-10時点)。

結論から書く。**外部連携(Slack/Notion等のMCP)を一切設定しない状態でも、`productivity`プラグインの「記憶(メモリ)」機能だけで、"ask todd to do the PSR for oracle"という社内略語だらけの依頼を正しく解読させることができた。** 同じ依頼文を、メモリファイルがある場合とない場合でそれぞれ実行し、応答がどう変わるかをBefore/Afterで比較した。

## knowledge-work-pluginsとは何か

公式READMEによれば、本リポジトリはAnthropicが自社のClaude Cowork(職種別アシスタント体験)およびClaude Code向けに用意した、職種特化のプラグイン集である。`productivity`・`sales`・`customer-support`・`product-management`・`marketing`・`legal`・`finance`・`data`・`enterprise-search`・`bio-research`・`cowork-plugin-management`の11種類に加え、Slack(Salesforce提供)やApollo.ioなどパートナー製のMCP連携プラグインも同梱されている。

各プラグインの実体は`.claude-plugin/plugin.json`・`skills/*/SKILL.md`・必要に応じた`.mcp.json`で、コードやビルド手順は無い。導入もClaude Code CLIから次の2コマンドで完了する。

```bash
claude plugin marketplace add anthropics/knowledge-work-plugins
claude plugin install productivity@knowledge-work-plugins
```

```
√ Successfully added marketplace: knowledge-work-plugins (declared in user settings)
√ Successfully installed plugin: productivity@knowledge-work-plugins (scope: user)
```

追加の有料APIキーやGPUは不要だった。今回は11種のうち`productivity`プラグインを選び、その中でも外部連携無しで検証できる`memory-management`スキルと`task-management`スキルの2つに絞って動作確認した(`/productivity:start`によるチャット・カレンダー等からの自動スキャンや、タスク管理用のビジュアルダッシュボードはそれぞれ外部コネクタ・ブラウザ表示が前提のため今回は対象外とした)。

## 検証: 社内略語の解読はBefore/Afterでどう変わるか

`memory-management`スキルは、`CLAUDE.md`(作業ディレクトリ直下)に人物・用語・プロジェクトの対応表を置いておくことで、"todd"や"PSR"のような社内略語をフルネーム・正式名称に解読する仕組みだ。SKILL.md自身に載っている例がまさに今回使った依頼文そのものだったので、これを実際に試した。

### Before: メモリファイルが無い状態

空のディレクトリ(`CLAUDE.md`無し)で、ツール利用そのものを禁止した上で次の依頼を投げた。

```bash
claude -p "ask todd to do the PSR for oracle. Just tell me in plain text what you \
understand this request to mean (who Todd is, what PSR means, what Oracle refers \
to) — do not use any tools, do not try to contact anyone, just answer in text." \
  --allowedTools "" --output-format json
```

応答(全文は`experiments/day-013/results.md`):

> **Todd**: I don't know who Todd is. ...
> **PSR**: Pipeline/Project Status Report, Problem Summary Report, Periodic Safety Report(pharma), Pre-Sentence Report(legal), Product/Platform Security Review...
> **Oracle**: Oracle the company, an Oracle product, or an internal project codenamed "Oracle"。

Todd・PSR・Oracleのどれも特定できず、PSRの候補を5つ列挙するだけで終わった。

### After: memory-managementスキルの記憶フォーマットを置いた場合

SKILL.mdが示す記憶フォーマットの例(人物表・用語表・プロジェクト表を持つ`CLAUDE.md`)を同じディレクトリに置き、**全く同じ依頼文**を再実行した。

応答:

> - **Todd:** Todd Martinez, the Finance lead.
> - **PSR:** Pipeline Status Report.
> - **Oracle:** The Oracle Systems deal, worth $2.3M and set to close in Q2.
>
> A few things I'm unsure about:
> - **Fit:** A pipeline report is usually a Sales task, and Greg Wilson is your Sales contact. Finance owning the Oracle PSR is plausible, since it's a large deal, but I'd like you to confirm Todd is the right person.

Todd・PSR・Oracleの3語とも`CLAUDE.md`の内容だけで正しく解読できた。さらに「パイプラインレポートは通常Salesの仕事のはずだが、Finance担当のTodd宛てで合っているか確認したい」という、記憶データ同士(Todd=Finance / PSRはSales文脈が多い)を突き合わせた整合性チェックが自発的に出てきたのは、単純な文字列置換ではなく記憶を文脈として扱っている様子が見えて興味深かった。

## 検証: task-managementスキルで自然文→TASKS.mdへの変換

同じディレクトリ(`CLAUDE.md`あり)で、今度はファイル書き込みのみ許可してタスク追加を依頼した。

```bash
claude -p "remind me to send the budget review to todd by friday" \
  --allowedTools "Read Write Edit" --output-format json
```

生成された`TASKS.md`:

```markdown
# Tasks

## Active
- [ ] Send budget review to Todd (Finance) — **due Fri 2026-10-16**

## Waiting On

## Someday

## Done
```

`task-management`スキルが指定するテンプレート(`# Tasks`/`## Active`/`## Waiting On`/`## Someday`/`## Done`の4セクション構成)通りに生成されており、「todd」は記憶ファイルから「Todd (Finance)」に解決され、「friday」は検証実行日(2026-10-11、日曜)から見た直近の金曜日`2026-10-16`に正しく変換されていた。

## 検証中に気づいたこと

今回のRoutine実行環境の中から入れ子で`claude -p`を呼ぶと、親セッションの`CLAUDE_CODE_SESSION_ID`等を引き継いでしまい、独立した検証にならないことに気づいた。最初の試行では応答の中に実際にアクセスできる別セッション名やSlackコネクタへの接続試行が出てきた(Slackは未接続のため403で失敗し実害は無かった)。これは`productivity`プラグイン自体の挙動ではなく、入れ子実行時の環境変数継承によるものなので、2回目以降は該当の環境変数を`env -u`で外し、`--allowedTools`でツールを最小限(または空)に絞ることで、独立したセッションとして比較できるようにした。再現手順は`experiments/day-013/README.md`に残している。

## まとめ

Apache-2.0で公開されたAnthropic公式のプラグイン集から`productivity`プラグインを実際に導入し、外部連携を一切使わない範囲(メモリ解読・タスク管理)で動作を確認した。`memory-management`スキルは、`CLAUDE.md`に置いた人物・用語・プロジェクトの対応表だけで社内略語を正しく解読し、`task-management`スキルは自然文の依頼を指定テンプレート通りの`TASKS.md`に変換した。いずれもコードやビルドを必要とせず、Markdown1枚を用意するだけで挙動が変わる点が、このプラグイン集の設計として面白かった。

- 出典: https://github.com/anthropics/knowledge-work-plugins (Apache-2.0)
- 検証したプラグイン: `productivity` v1.3.1
