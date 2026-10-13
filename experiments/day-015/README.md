# Day 015: google/skills (Google公式Agent Skillsライブラリ) 検証

対象: https://github.com/google/skills (Apache-2.0)
比較対象: day-013 (https://github.com/anthropics/knowledge-work-plugins)

詳細な検証結果・Before/After比較・結論は [`results.md`](./results.md) を参照。

## 再現手順

前提: Node.js (npxが使えること)、Claude Code CLI、インターネット接続
(`raw.githubusercontent.com`・`api.github.com`への到達性が必要)。

### 1. スキルの一覧確認・インストール

```bash
mkdir sandbox && cd sandbox

# リポジトリ全体をclone(SKILL.mdの構成確認・LICENSE確認用)
git clone --depth 1 https://github.com/google/skills.git google-skills-repo

# npx skills CLIで個別スキルをインストール(Claude Code用)
npx -y skills@latest add google/skills -s finding-google-skills -a claude-code -y
# => ./.claude/skills/finding-google-skills/SKILL.md が生成される
```

### 2. Before/After比較(`finding-google-skills`の効果測定)

Before(スキル無し、ツール禁止):

```bash
cd before-test   # .claude/skills が無い空ディレクトリ
env -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_REMOTE_SESSION_ID -u CLAUDE_CODE_CHILD_SESSION \
    -u CLAUDE_CODE_MESSAGING_SOCKET -u CLAUDE_CODE_MESSAGING_TOKEN \
claude -p "I have an AI agent instrumented with OpenTelemetry deployed on Cloud Run. I want to \
set up monitoring alerts for it covering latency, errors, cost, safety, and quality. According \
to official Google guidance, what alerts should I configure, in what output format, and are \
there any caveats? Do not use any tools, just answer in plain text from what you know." \
  --allowedTools "" --output-format json
```

After(`finding-google-skills`インストール済みディレクトリ内、Skill/Bashのcurlのみ許可):

```bash
cd install-test   # 手順1でインストールした .claude/skills/finding-google-skills があるディレクトリ
env -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_REMOTE_SESSION_ID -u CLAUDE_CODE_CHILD_SESSION \
    -u CLAUDE_CODE_MESSAGING_SOCKET -u CLAUDE_CODE_MESSAGING_TOKEN \
claude -p "(同じ質問文) + use the Skill tool / any skill you have access to, and Bash only for \
read-only curl lookups of public documentation if needed. Do not run gcloud/terraform/python, \
do not write any files." \
  --allowedTools "Skill Bash(curl:*) Read" --output-format json
```

実際の実行結果(`result`フィールド全文)とメタ情報(`total_cost_usd`・`duration_ms`・`num_turns`)は
`logs/before_run.json` / `logs/after_run.json` にそのまま保存している。

## 検証範囲外にしたもの(理由)

- `plugins/cloud/google-cloud-developer` の `developer-knowledge` MCPサーバー: `google_credentials`
  認証(GCPプロジェクト)が必須のため、有料APIキー不要方針により今回は未検証。
- `agent-platform-alert-configuration` スキルの実際の `gcloud`/`terraform apply` によるアラート
  デプロイ: 実GCPプロジェクト・課金が前提のため、SKILL.mdの内容を正しく読み取れるかの確認までに留めた。
