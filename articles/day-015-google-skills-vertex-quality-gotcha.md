---
title: "Google公式Agent Skillsライブラリ「google/skills」の検索ルーターを試し、anthropics版と並べてみた"
emoji: "🧭"
type: "tech"
topics: ["ai", "claudecode", "oss", "googlecloud", "llm"]
published: false
---

筆者は海外のAI関連ニュースを毎日1本検証して発信するチャレンジの15日目として、Googleが公開した[google/skills](https://github.com/google/skills)を実際にインストールして動かしてみた。Google Cloud/Ads/Analytics等の公式Agent Skillsを集めたリポジトリ(Apache-2.0)で、本稿執筆時点で`skills/`配下に155件、プラグイン内に5件、計160件のSKILL.mdが収録されている。筆者が検索した範囲ではZenn・Qiita・noteのいずれにも日本語での一次紹介記事は見つからなかった(2026-10-12時点)。

13日目には[anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)(Anthropic公式のプラグイン集)を検証した。今回は同じ「公式配布のAgent Skills」という土台のうえで、両者の配布のされ方・構成・導入体験がどう違うかを実測して比較する。

結論から書く。**google/skillsの`finding-google-skills`スキルは中身を持たない「検索ルーター」で、実行時に`index.json`(155件分のメタデータ)をネットワーク越しに取得し、該当するスキルだけを追加で取りに行く設計だった。** 同じ質問を「ルーター無し」と「ルーター有り」で投げ比べたところ、ルーター有りの方だけが「Cloud Run単体ではQuality系アラートが動かない(Vertex AI Online Monitors依存のため)」という、汎用知識では出てこない具体的な制約を正しく引き出した。

## google/skillsとは何か

公式READMEによれば、本リポジトリはGoogle Cloud/Gemini関連プロダクト向けのAgent Skillsとプラグインを集めた公式リポジトリである。構成は大きく2つに分かれる。

- `skills/`(155件): `ads`・`analytics`・`cloud`・`developers`・`identity`の5カテゴリに分かれた、素のSKILL.mdファイル群。スラッシュコマンドは持たず、「読んで従うだけ」のドキュメント型スキル。
- `plugins/`(2件、5スキルを内包): `.claude-plugin/plugin.json`・`gemini-extension.json`・`.codex-plugin/plugin.json`を同梱し、Claude Code/Gemini CLI/Codexそれぞれに対応するマルチターゲット構成。`google-cloud-developer`プラグインは`developer-knowledge`というMCPサーバー(`google_credentials`認証必須)も同梱していた。

ライセンスはリポジトリ直下に`LICENSE`が1つのみで、README「## License」節に「Apache 2.0 license. See the `LICENSE` file for details.」と明記されている。`skills/`と`plugins/`を分けた別ライセンスは無く、day-013のanthropics/knowledge-work-pluginsと同じ単一LICENSE方式だった。

導入は`npx skills`というサードパーティ製CLI(v1.7.2、Claude Code/Codex/Antigravity等マルチエージェント対応)から行う。

```bash
npx -y skills@latest add google/skills -s finding-google-skills -a claude-code -y
```

```
o  Source: https://github.com/google/skills.git
o  Repository cloned
o  Found 155 skills
•  Selected 1 skill: finding-google-skills

o  Installed 1 skill --------------------------+
|  ✓ finding-google-skills (copied)            |
|    → ./.claude/skills/finding-google-skills  |
+----------------------------------------------+
```

`skills-lock.json`に取得元パス(`skills/developers/finding-google-skills/SKILL.md`)とハッシュが記録され、生成されたファイルは`git clone`した本家と完全一致していた(copy配布、symlinkではない)。有料APIキーは不要、追加のビルドも不要だった。

おもしろかったのは、CLIが報告した「Found 155 skills」という数が、`find . -iname SKILL.md`で数えた`skills/`配下のファイル数(155件)とは一致するものの、`plugins/`配下に埋め込まれた5件は含んでいないことだった。つまりこのCLIの発見対象は`skills/`ディレクトリの素のSKILL.mdのみで、プラグイン内のSKILL.mdはCLIの検索・インストール対象外ということになる。

## day-013(anthropics/knowledge-work-plugins)との比較

| 観点 | anthropics/knowledge-work-plugins (day-013) | google/skills (day-015) |
|---|---|---|
| 導入コマンド | Claude Code組み込みのプラグイン機構(`claude plugin marketplace add` → `claude plugin install`) | サードパーティCLI `npx skills add`(SKILL.md単位、`-s`で個別選択可能) |
| 導入単位 | プラグイン単位(スキル+スラッシュコマンド+HTMLダッシュボードのセット) | SKILL.md単位。スラッシュコマンドは基本持たない |
| 構成 | 11種のプラグイン、各プラグインは2〜数個のスキル+スラッシュコマンド | 155件の素のスキル+2件のマルチエージェント向けプラグイン(MCPサーバー同梱) |
| ロード方式 | 常駐(ローカルファイルとして最初から読み込まれる) | オンデマンド(`finding-google-skills`のような一部スキルは実行時にネットワークから`index.json`を取得) |
| ライセンス | Apache-2.0、単一LICENSE | Apache-2.0、単一LICENSE(同方式) |

対象読者という観点で見ると、anthropics版は「自分のローカルディレクトリに記憶・タスクを溜める個人向けナレッジワーク補助」、google版は「製品ドキュメントを都度引き込む、クラウド製品の意思決定支援カタログ」という、同じ「公式Agent Skills配布」でも設計思想が対照的だった。

## 検証: `finding-google-skills`ルーターの効果をBefore/Afterで測る

`finding-google-skills`自体はコンテンツを持たないルーターなので、効果を測るには実際に動かして比較するのが一番わかりやすい。day-013と同じ手法(`claude -p`非対話モード、親セッションの環境変数を`env -u`で外して独立させる)で、同一の質問を「ルーター無し・ツール禁止」と「ルーター有り・Skill/curlのみ許可」で2回投げた。

質問文(共通):

> I have an AI agent instrumented with OpenTelemetry deployed on Cloud Run. I want to set up monitoring alerts for it covering latency, errors, cost, safety, and quality. According to official Google guidance, what alerts should I configure, in what output format, and are there any caveats?

### Before: ルーター無し、ツール禁止

```bash
env -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_REMOTE_SESSION_ID -u CLAUDE_CODE_CHILD_SESSION \
    -u CLAUDE_CODE_MESSAGING_SOCKET -u CLAUDE_CODE_MESSAGING_TOKEN \
claude -p "(上記質問 + Do not use any tools, just answer in plain text from what you know.)" \
  --allowedTools "" --output-format json
```

応答の冒頭(全文は`experiments/day-015/logs/before_run.json`):

> I don't know of a single Google document that prescribes an official alert list and output format for this setup, and I'd rather not invent one.

そのうえでCloud Run組み込みメトリクスやOTelのGenAIセマンティックコンベンションから類推した、汎用的なアラート案(PromQL/MQL、「YAMLでもTerraformでもいい」)を提示した。Qualityについては「評価パイプラインを自分で構築する必要があり、そのままでは動かない」という一般論で終わった。幻覚ではなく正直な前置きはあったが、具体性は乏しい。

### After: `finding-google-skills`インストール済み、Skill/curlのみ許可

```bash
env -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_REMOTE_SESSION_ID -u CLAUDE_CODE_CHILD_SESSION \
    -u CLAUDE_CODE_MESSAGING_SOCKET -u CLAUDE_CODE_MESSAGING_TOKEN \
claude -p "(同じ質問 + use the Skill tool / any skill you have access to, and Bash only for \
  read-only curl lookups of public documentation. Do not run gcloud/terraform/python, do not \
  write any files.)" \
  --allowedTools "Skill Bash(curl:*) Read" --output-format json
```

応答の冒頭(全文は`experiments/day-015/logs/after_run.json`):

> This comes from Google's published skill `agent-platform-alert-configuration`, from the `google/skills` catalog. I also checked `cloud-run-alert-configuration`.

今度は具体的に以下を正しく引き出していた。

- **12件のポリシーを5カテゴリで「exactly」指定**(Reliability 5件・Cost 1件・Safety 1件・Quality 3件・Security 1件)という、スキル本文のルールそのまま。
- **出力形式はTerraformのみ**、Reliability系はPromQL・Safety/Security系はSQL(`condition_sql`、provider 6.0.0以降が必要)という言語の使い分け。
- 最も重要なキャビアット: **「Quality alerts won't work on Cloud Run」**。Reliability/Cost/Safety/Securityは汎用OTelメトリクスでCloud Run等どのランタイムでも動くが、QualityはVertex AI Online Monitorsに厳密に紐付いているため、Cloud Run単体では動かないという、スキル本文のdescriptionに書かれた制約をそのまま正しく引用した。Beforeの回答は「評価パイプラインを自作する必要がある」という一般論止まりで、Vertex AIへの依存という具体的な製品的理由までは言及していなかった。
- `cloud-run-alert-configuration`という別スキルの存在にも気づき、Cloud Run自体のインフラ向けアラート(5xx可用性SLO・P95/P99レイテンシ等)との役割分担を説明していた。

実行メタ情報を比べると、Beforeは`num_turns=1`(ツール呼び出し0回)に対し、Afterは`num_turns=5`で、`total_cost_usd`もBeforeの0.076ドルからAfterの0.172ドルに増えていた。`index.json`(約75KB、155件分のメタデータ)の取得→絞り込み→該当する2スキルのSKILL.mdの追加取得という複数ステップが実際に発生したためだ。

## 検証範囲外にしたもの

`agent-platform-alert-configuration`スキル自体はPythonの補助スクリプト実行・GCPプロジェクトID必須・課金の明示確認必須・Terraform lintまで求める重厚な設計で、実際にアラートをデプロイする工程は有料GCPリソースの作成を伴う。このチャレンジの方針(有料APIキー・GCPリソース作成を前提にしない)に従い、今回は「正しくルーティングされ、正しい内容を読み取れるか」という読み取り部分のみを検証範囲とした。同様に、`google-cloud-developer`プラグインの`developer-knowledge`MCPサーバーは`google_credentials`認証が必須のため未検証とした。

## まとめ

google/skillsをインストールし、`finding-google-skills`ルーターの効果を実測した。中身を持たないルーター1枚が、ネットワーク越しに正しいスキルを引き当て、「Quality系アラートはCloud Run単体では動かない」という具体的な製品知識を正しく引き出す様子を確認できた。day-013のanthropics/knowledge-work-pluginsが「ローカルに常駐する個人向け記憶」だったのに対し、google/skillsは「都度ネットワークから取りに行く製品カタログ」という対照的な設計だった点が、同じ「公式Agent Skills」という枠組みの中でも興味深い違いだった。

- 出典: https://github.com/google/skills (Apache-2.0)
- 比較対象: https://github.com/anthropics/knowledge-work-plugins (Apache-2.0, day-013)
- 検証したスキル: `finding-google-skills` v1.1.0
