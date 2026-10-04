# Vendored code from world-model-self-organized-criticality

このディレクトリの `synthetic_graph_world.py` と `backends_ctwm.py` は以下のリポジトリから
**無改変で**コピーしたもの(MIT License)。

- 出典: https://github.com/Hik289/world-model-self-organized-criticality
- 論文: Song & Cai, "Heavy-Tailed Memory Traces in Long-Horizon Language Agents" (arXiv:2610.00010)
- ライセンス: MIT License(`LICENSE` に原文を同梱)

day-006の検証では、この2ファイル(合成グラフ世界の生成コードとCore-Tail World Model (CTWM) の
メモリコントローラ本体)をそのまま再利用し、`../run_prediction_loop.py` から呼び出している。
LLMポリシー部分(本家は外部LLM API前提)は使用せず、次状態予測だけをClaude Code自身が
手動ループで代替した(詳細は `../README.md` と `../results.md` を参照)。
