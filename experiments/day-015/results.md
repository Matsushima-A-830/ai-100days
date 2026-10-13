# Day 015 results

対象: https://github.com/google/skills (Apache-2.0、本日時点 155 skills + 5 skills(プラグイン内) = 160 SKILL.md、GitHub Trending Python 2026-10-12、21.2k star)
比較対象: day-013で検証した https://github.com/anthropics/knowledge-work-plugins (Apache-2.0)
検証環境: Claude Code CLI 2.1.296、Node.js v22.22.0 / npm 10.9.4、`npx skills@latest`(v1.7.2)、`claude -p`(非対話モード)

## 0. 導入ログ

```
$ npx -y skills@latest add google/skills -s finding-google-skills -a claude-code -y

•   claude-code_2-1-296_agent  Agent detected — installing non-interactively
o  Source: https://github.com/google/skills.git
•  Cloning repository… (…) o  Repository cloned
•  Discovering skills… o  Found 155 skills
•  Selected 1 skill: finding-google-skills

o  Installation Summary -------------------+
|                                          |
|  ./.agents/skills/finding-google-skills  |
|    copy → Claude Code                    |
|                                          |
+------------------------------------------+
o  Installation complete

o  Installed 1 skill --------------------------+
|                                              |
|  ✓ finding-google-skills (copied)            |
|    → ./.claude/skills/finding-google-skills  |
|                                              |
+----------------------------------------------+

—  Done!  Review skills before use; they run with full agent permissions.
```

実行後、`./.claude/skills/finding-google-skills/SKILL.md` が生成され、`skills-lock.json` に
`source: "google/skills"`・`skillPath: "skills/developers/finding-google-skills/SKILL.md"`・
`computedHash` が記録された。インストールされたファイルは `git clone` 元の同パス
(`skills/developers/finding-google-skills/SKILL.md`)と `diff` で完全一致(コピー配布、symlinkではない)。
有料APIキーは不要、ビルドも不要だった。

## 1. day-013(anthropics/knowledge-work-plugins)との比較

| 観点 | day-013: anthropics/knowledge-work-plugins | day-015: google/skills |
|---|---|---|
| 導入コマンド | `claude plugin marketplace add` → `claude plugin install productivity@knowledge-work-plugins` (Claude Code組み込みのプラグイン機構) | `npx skills add google/skills -s <skill名>` (サードパーティ製CLI `skills`、v1.7.2。Claude Code/Codex/Antigravity等マルチエージェント対応) |
| 導入単位 | プラグイン単位(1プラグイン=複数スキル+スラッシュコマンド+HTML等のセット) | SKILL.md単位(1スキル=1ファイル、`-s`で個別選択可能。`--all`で全160件も可) |
| 構成・粒度 | `productivity`プラグインは2スキル(task-management, memory-management)+2スラッシュコマンド(`/productivity:start`, `/productivity:update`)+`dashboard.html`(ブラウザ表示用UI)のセット。コードやビルド手順なし。 | リポジトリ全体は `skills/`(155件、素のSKILL.md、スラッシュコマンドなし)と `plugins/`(2件、マルチエージェント向けplugin.json+MCPサーバー定義+スラッシュコマンド相当のrulesファイルを含む複合パッケージ)の二階建て。`skills/`配下は基本的に「読んで従うだけ」のドキュメント型スキルで、スラッシュコマンドは持たない。`plugins/cloud/google-cloud-developer`だけは`.claude-plugin/plugin.json`・`gemini-extension.json`・`.codex-plugin/plugin.json`を同梱し、Claude Code/Gemini CLI/Codexそれぞれに対応するマルチターゲット構成(MCPサーバー`developer-knowledge`は`google_credentials`認証必須のため今回は検証対象外)。 |
| ライセンス | Apache-2.0。リポジトリ直下に`LICENSE`。 | Apache-2.0。リポジトリ直下に`LICENSE`1つのみで、README「## License」節が「Apache 2.0 license. See the `LICENSE` file for details.」と明記。`skills/`と`plugins/`の両方を1つのLICENSEが対象にしており、スコープ分割はない(day-013と同じ単一LICENSE方式)。 |
| 「何を売りにしているか」の違い(結論) | 自分のローカルディレクトリに記憶・タスクを溜める「個人向けナレッジワーク補助」 | Google Cloud/Ads/Analytics等、製品ごとの公式ドキュメントをオンデマンドで引き込む「製品カタログのルーター」。`finding-google-skills`自体はコンテンツを持たず、`index.json`(155件のメタデータ、約75KB)を実行時に`curl`で取得し、descriptionマッチングで該当スキルだけ追加フェッチする設計(day-013のような「常時ロードされるローカルファイル」ではなく「都度ネットワーク越しに取りに行くインデックス」)。 |

## 2. Before/After検証: finding-google-skillsスキルの効果

day-013と同じ手法(`claude -p`非対話モード、`CLAUDE_CODE_SESSION_ID`等を`env -u`で外して
親セッションから独立させる)で、同一の質問を「スキル無し・ツール禁止」と
「`finding-google-skills`インストール済み・Skill/Bash(curl)のみ許可」で2回投げて比較した。

質問文(共通):

> I have an AI agent instrumented with OpenTelemetry deployed on Cloud Run. I want to set up
> monitoring alerts for it covering latency, errors, cost, safety, and quality. According to
> official Google guidance, what alerts should I configure, in what output format, and are
> there any caveats?

### Before(スキル無し、`--allowedTools ""`)

実行コマンド:
```bash
env -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_REMOTE_SESSION_ID -u CLAUDE_CODE_CHILD_SESSION \
    -u CLAUDE_CODE_MESSAGING_SOCKET -u CLAUDE_CODE_MESSAGING_TOKEN \
claude -p "(上記質問 + Do not use any tools, just answer in plain text from what you know.)" \
  --allowedTools "" --output-format json
```

応答の要旨(全文は`before_run2.json`):
> I don't know of a single Google document that prescribes an official alert list and output
> format for this setup, and I'd rather not invent one. What follows is what I know of Google's
> building blocks, plus a reasonable alert set built from them.

その後、Cloud Run組み込みメトリクス・OTel GenAIセマンティックコンベンション・Vertex AI評価サービス等
から類推した**汎用的な**アラート案(PromQL/MQL、YAML or Terraform)を提示。Qualityについては
「評価パイプラインを自分で構築する必要があり、そのままでは動かない」という一般論で終わった。
出力形式は「JSON/YAML/Terraformのどれでもいい」という曖昧な案。

実行メタ情報: `total_cost_usd=0.0756574`, `duration_ms=15244`, `num_turns=1`, `permission_denials=[]`
(`before_run2.json`に保存)。

### After(`finding-google-skills`インストール済み、`--allowedTools "Skill Bash(curl:*) Read"`)

実行コマンド:
```bash
env -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_REMOTE_SESSION_ID -u CLAUDE_CODE_CHILD_SESSION \
    -u CLAUDE_CODE_MESSAGING_SOCKET -u CLAUDE_CODE_MESSAGING_TOKEN \
claude -p "(同じ質問 + use the Skill tool / any skill you have access to, and Bash only for
  read-only curl lookups of public documentation if needed. Do not run gcloud/terraform/python,
  do not write any files.)" \
  --allowedTools "Skill Bash(curl:*) Read" --output-format json
```

応答の要旨(全文は`after_run.json`):
> This comes from Google's published skill `agent-platform-alert-configuration`, from the
> `google/skills` catalog. I also checked `cloud-run-alert-configuration`.

具体的に以下を正しく引き出していた:

- **12件のポリシーを5カテゴリに分けて「exactly」指定**(Reliability 5件・Cost 1件・Safety 1件・
  Quality 3件・Security 1件)という、スキル本文のルールそのままの構成。
- **出力形式はTerraformのみ**(`.tf`、`alerts.tf`/`variables.tf`)、Reliability系はPromQL・
  Safety/Security/Model/Tool call系はSQL(`condition_sql`、provider 6.0.0以降が必要)、Qualityは
  標準しきい値条件、という言語の使い分け。
- **最も重要なキャビアット**: 「Quality alerts won't work on Cloud Run」——Reliability/Cost/Safety/
  Securityは汎用OTelメトリクスでCloud Run等どのランタイムでも動くが、QualityはVertex AI Online
  Monitorsに**厳密に紐付いており**、Cloud Run単体では動かない、という`agent-platform-alert-configuration`
  のSKILL.md本文(description内の「NOTE」)をそのまま正しく引用していた。Beforeの回答は
  Qualityについて「評価パイプラインを自作する必要がある」という一般論止まりで、
  「Vertex AI Online Monitorsへの依存」という具体的な製品的理由までは言及していなかった。
- 追加で`cloud-run-alert-configuration`(Cloud Run自体のインフラ向けアラート: 5xx可用性SLO・
  P95/P99レイテンシ・CPU/メモリ使用率等)という**別スキル**の存在にも気づき、役割分担を説明していた。
- Online Monitor作成やTelemetry exportには追加の課金が発生する点、ユーザーの明示確認が必須な点も
  スキル本文のまま正確に再現していた。

実行メタ情報: `total_cost_usd=0.17194769999999998`, `duration_ms=19423`, `num_turns=5`, `permission_denials=[]`
(`after_run.json`に保存。Beforeよりコスト・ターン数が増えているのは、`index.json`〈約75KB、155件分の
メタデータ〉の取得→絞り込み→該当する2スキルのSKILL.mdの追加取得、という複数ステップの
ツール呼び出しが実際に発生したため)。

### わかったこと

- `finding-google-skills`自体は中身を持たない「ルーター」スキルで、効果を測るには実際にネットワーク越しに
  `index.json`(`https://raw.githubusercontent.com/google/skills/main/index.json`)と、マッチした
  個別スキルのSKILL.mdを取得できる環境が必須(有料APIキーは不要、ただしアウトバウンドHTTPS到達性が必要。
  このRoutine実行環境のプロキシ経由で`curl`が到達できることは事前に確認済み)。
- Before/Afterの差は「嘘をつくかどうか」ではなく「どこまで具体的か」の差だった。Beforeも
  「公式文書を知らない」と正直に前置きしており幻覚ではなかったが、具体的なポリシー数・
  出力形式の強制(Terraformのみ)・Qualityアラートの製品的な動作条件という、
  汎用知識だけでは出てこない具体性はAfterでしか得られなかった。
- `agent-platform-alert-configuration`のSKILL.md自体は非常に重厚(Python補助スクリプト実行・
  GCPプロジェクトID必須・課金確認必須・Terraform lint等)で、実際にアラートを**デプロイする**
  工程は有料GCPリソース作成を伴うため、CLAUDE.mdの「有料APIキー不要」方針に従い今回は
  「正しくルーティングされ、正しい内容を読み取れるか」という読み取り部分のみを検証範囲とした
  (実際の`gcloud`/`terraform apply`は実行していない)。

## 3. 結論(一言)

anthropics/knowledge-work-pluginsは「ローカルファイルに記憶・タスクを溜める個人用プラグイン」、
google/skillsは「製品ドキュメントを都度ネットワークから取りに行くカタログ型ルーター」であり、
配布単位(プラグイン vs SKILL.md単体)・ロード方式(常駐 vs オンデマンド取得)・対象読者
(個人の生産性 vs クラウド製品の意思決定支援)のいずれも異なる、同じ「公式Agent Skills配布」でも
設計思想が対照的な2例だった。
