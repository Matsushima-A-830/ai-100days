# Day 008: Mem++(非破壊メモリ)の概念再現

対象: https://arxiv.org/abs/2610.02002 / https://github.com/AIDAChip-Inc/mem-plus-plus (Apache-2.0)

**重要な注意:** サンドボックスの安全分類器により実リポジトリのコード(`uv sync`以降)は
実行できなかった。経緯は `results.md` を参照。ここにあるのは実リポジトリを使わず、
論文/READMEのアルゴリズム説明を読んで理解した上で筆者が独自に書いた最小再現コードの実行手順。

## 再現手順

```bash
cd experiments/day-008
python3 compare_memory.py
```

依存関係: Python 3標準ライブラリのみ(追加インストール不要)。

## 中身

- `compare_memory.py`: 「要約・上書き型メモリ」(`DestructiveSummaryMemory`)と
  「非破壊+as-ofフィルタ型メモリ」(`NonDestructiveMemory`)を、架空の社内決定記録
  (検索基盤/デプロイ先クラウド/コードレビュー方針、各3回更新)に対する9つのas-ofクエリで比較する。
- `results.md`: 実行ログと、何を検証できて何を検証できなかったかの正直な記録。
