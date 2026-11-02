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

## ローカル検証: `/start`から`/dev-story`まで実際に動かした

Routine実行環境では、クローンしたテンプレート自身のコード(`.claude/hooks/*.sh`の直接実行、
および `claude -p "/start" --dangerously-skip-permissions` のようなネストしたClaude Codeセッションの
起動)が、実行環境側の自動モード分類器によって `[Code from External]` / `[Create Unsafe Agents]` という
理由でブロックされ、実行できなかった(Routine環境固有の制約。detailsはresults.md参照)。

そのためローカル(手元のPC、通常の対話的 `claude` セッション)で改めてクローンし
(`experiments/day-035/ccgs-trial/`)、`/start` → `/brainstorm` → `/setup-engine` →
`/create-stories` → `/dev-story` × 6 → `/story-done` × 6 という一連のワークフローを実際に最後まで
動かして、衛星リレー局修理ゲーム「Signal Lost」(Unity, C#)を実際にプレイできる状態まで作った。

- 生成した設計書・ストーリーファイル・コード本体: `signal-lost-game/`
- 途中で遭遇した詰まりどころ(WSL上でUnityエディタがプロジェクトを開けなかった件、Playモード
  突入時のドメインリロードでスプライト参照が消えた件など)を含む全記録: `results.md` §4

## 見つけたこと(詳細はresults.md)

§1-3はRoutine環境での構造検証とClaude Code自体の「CLAUDE.md自動検出」の挙動、§4がローカルでの
実際のワークフロー検証(今回の検証の本題)。
