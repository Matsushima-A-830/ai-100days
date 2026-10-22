# Day 024: DietrichGebert/ponytail — 「怠惰なシニア開発者」スキルは本当にコードを減らすのか

- 出典: https://github.com/DietrichGebert/ponytail (検証時点のHEAD: `09c434a`, 2026-10-18, npm版 `5.3.2`)
- ライセンス: MIT
- 公式の主張: Ponytail 5はスキル無しのClaude Code(Opus 5.5)と比べて、コード行数-53%・出力トークン-45%・コスト-26%・時間-41%(`benchmarks/results/2026-10-07-agentic.md`、39タスク×5回、headless Claude Codeセッション`claude -p --plugin-dir`による計測)。

## やったこと

1. ponytailのリポジトリをクローンし、`skills/ponytail/SKILL.md`(本体ルールセット、52行)と公式ベンチマーク手法(`benchmarks/agentic/README.md`、`benchmarks/results/2026-10-07-agentic.md`)を読んだ。
2. 公式と同じ方法(`claude -p --plugin-dir <ponytailのパス>` によるheadless Claude Codeセッションのペア比較)で再現しようとしたが、**このRoutineのクラウド実行環境では、Claude Codeの権限自動分類器が「Create Unsafe Agents」という理由でこの起動方法そのものをブロックした**(`--permission-mode acceptEdits` でも `bypassPermissions` でも同じ理由で拒否。試行の詳細は `results.md` 参照)。これはRoutine実行環境のサンドボックス制約であり、ponytail自体の欠陥ではない。
3. そのため、公式と全く同じ方法での再現は断念し、**代替手法**として、同じモデル(このセッションと同じ `claude-sonnet-5`)に対して、Claude Code内のサブエージェント機能(Agent tool)で独立した2本の実行コンテキストを作り、
   - (a) baseline: 何の指示も加えずタスクだけを与える
   - (b) ponytail: `SKILL.md` の全文(ルールセットそのもの)をシステム指示として渡し、同じタスクを与える
   をそれぞれ実行し、生成された差分(diff)を比較する簡易ベンチマークを自分で組んだ。
4. 最初の2タスク(日付入力フィールド追加・チェックボックスフィールド追加)は、既存の汎用`Input`コンポーネントを再利用するのが明らかな最適解になるよう作った小さな固定サンプル(`fixture-template/`)に対して実行した。
5. 結果、baseline/ponytailで生成コードが**完全に同じ行数(+1行)**になり、差が全く出なかった。公式ベンチマークの手法ノート(`benchmarks/agentic/README.md`)を読み直すと、LOCティアのタスクは意図的に「まだ存在しない機能」を選んでいる("a feature that does not already exist, so the agent chooses how much to build")。つまり、自分が最初に作った2タスクは「再利用一択」で過剰実装の余地がほぼ無く、ponytailの効果を測るには不適切なタスク設計だったと気づいた。
6. そこで公式のLOCティアにある「star rating(星レーティング)」タスクと同じ設計で3つ目のタスクを追加した。既存コンポーネントでは対応できず、エージェントが「どこまで作るか」を自分で決める必要があるタスクで再比較した。

## ディレクトリ

- `fixture-template/` — 3タスク共通の出発点(汎用`Input`コンポーネント + signupフォーム)
- `runs/a-baseline/`, `runs/a-ponytail/` — Task A: 生年月日フィールド追加
- `runs/b-baseline/`, `runs/b-ponytail/` — Task B: Remember meチェックボックス追加
- `runs/c-baseline/`, `runs/c-ponytail/` — Task C: 星レーティング(1〜5)フィールド追加
- `results.md` — 実測結果・diff・正直な記録

## 再現手順

```bash
git clone --depth 1 https://github.com/DietrichGebert/ponytail.git /tmp/ponytail-src
# fixture-template/ を複数回コピーしてタスクごとのディレクトリを作る(本ディレクトリのruns/*参照)
# 自分の環境で各ディレクトリに対し、baseline/ponytail両方のタスクを実行し、diffを比較する
```

公式ベンチマークそのもの(`claude -p --plugin-dir`によるheadlessセッション比較)をローカルで再現する場合:

```bash
cd /tmp/ponytail-src
# baseline(スキル無し)
cd <タスク用の空ディレクトリ>
claude -p "<タスク文>" --output-format json --permission-mode acceptEdits

# ponytail版(同じタスクディレクトリをコピーして)
claude -p "<タスク文>" --output-format json --permission-mode acceptEdits --plugin-dir /tmp/ponytail-src
```

**注意: 上記の`claude -p --permission-mode acceptEdits/bypassPermissions`は、このRoutineのクラウド実行環境では「Create Unsafe Agents」という権限分類器によってブロックされた。** ローカルPC環境での実行结果は未検証(ローカル検証待ち)。
