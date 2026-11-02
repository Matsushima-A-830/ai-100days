# Day 035: Claude Code Game Studios を検証する

対象: [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)(MIT)

Claude Codeの1セッションを49体のサブエージェント・74個のスラッシュコマンド形式スキル・15個のフック・
14個のパス限定ルール・62個のドキュメントテンプレートからなる「ゲーム開発スタジオ」として動かすテンプレート。

## 再現手順(このRoutine環境で行ったこと)

```bash
mkdir -p experiments/day-035
cd experiments/day-035
git clone --depth 1 https://github.com/Donchitos/Claude-Code-Game-Studios.git template
cd template
ls .claude/agents | wc -l   # => 49
ls .claude/skills | wc -l   # => 74
ls .claude/rules  | wc -l   # => 14
find .claude/docs/templates -maxdepth 1 -type f | wc -l  # => 63
grep -c '\.sh"' .claude/settings.json  # hooksブロック内の登録数を目視確認 => 15
```

検証後、クローンはサードパーティのネストしたgitリポジトリをそのままコミットするのは適切でないため
`rm -rf experiments/day-035/template` で削除済み(ライセンス・出典はこのREADME/results.mdに明記)。

## ローカル検証が必要(人間による追加確認をお願いします)

このRoutine実行環境では、クローンしたテンプレート自身のコード(`.claude/hooks/*.sh`の直接実行、
および `claude -p "/start" --dangerously-skip-permissions` のようなネストしたClaude Codeセッションの
起動)が、実行環境側の自動モード分類器によって `[Code from External]` / `[Create Unsafe Agents]` という
理由でブロックされ、実行できなかった(Routine環境固有の制約。detailsはresults.md参照)。

したがって、このテンプレートの核心である「`/start`→`/setup-engine`→`/brainstorm`→`/create-stories`→
`/dev-story`という49エージェント・74スキルの実際のワークフロー」はローカルでの再現確認が必要です。

ローカルでの再現コマンド(手元のPCで、通常の対話的 `claude` セッションとして):

```bash
git clone https://github.com/Donchitos/Claude-Code-Game-Studios.git ccgs-trial
cd ccgs-trial
claude
# セッション内で:
/start
# Phase 2で A) No idea yet / B) Vague idea / C) Clear concept / D) Existing work を聞かれる想定
# 続けて /setup-engine godot 4.7 、 /brainstorm などを試す
```

## 見つけたこと(詳細はresults.md)

このRoutine環境でテンプレート自体のコード実行がブロックされたため、構造の検証と、作業中に偶然観測した
Claude Code自体の「CLAUDE.md自動検出」の挙動が今回の主な検証結果になった。
