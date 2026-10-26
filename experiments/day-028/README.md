# Day 028: 「要約・変異型メモリ」vs「追記のみメモリ」vs「素朴なRaw-RAG」の縮小再現

検証対象論文: "Is Complex Agentic Memory Always Needed? Naive RAG Is Stronger Than We Thought"
出典: https://huggingface.co/papers/2610.30755 (arXiv:2610.30755)

著者独自実装のコード公開は確認できなかったため、論文の主張(変異型メモリの害・素朴なRAGの
強さ)をごく小さい自作データで概念実証する縮小版を実装した。追加のAPIキー・GPUは使っていない。

## 含まれているファイル

- `datasets.py`: 自作の架空会話ログ3本(それぞれ20〜25ターン)と、採点用の質問セット
  (QUESTIONS、current=最新の値を問う質問 / historical=上書き済みの過去の値を問う質問)
- `memory_methods.py`: 3種類のメモリ実装(MutatingSummaryMemory / AppendOnlyMemory /
  RawRAGMemory、自作TF-IDF検索含む)
- `run_experiment.py`: メインの比較実験スクリプト
- `ablation_rag.py`: RawRAGMemoryの検索精度を左右する要因(発言者ラベルの有無・簡易語幹
  処理・top_k)を切り分けるアブレーション
- `run_output.log` / `ablation_output.log`: 実際の実行ログ(そのまま保存)
- `results.md`: 結果と分析(再現できた点・できなかった点を正直に記録)

## 再現手順

Python 3.11、追加ライブラリ不要(標準ライブラリのみ)。

```bash
cd experiments/day-028
python3 run_experiment.py      # メインの実験(3手法 × 24問の比較)
python3 ablation_rag.py        # RawRAGの検索精度アブレーション
```

## 結果の要点

- 「メモリの変異(上書き)は過去の情報を失わせる」という論文の核心的な指摘は再現できた:
  上書き型メモリは過去の値を聞く質問(historical)に16.67%しか正答できず、同じ抽出ロジックで
  追記のみにしたメモリは100%正答した。
- 「素朴なRaw-RAGが最強」という見出しの結果は、今回の縮小実装・小規模データでは再現しな
  かった(RawRAGはcurrent 25.00%、historical 33.33%で、構造化メモリより劣った)。原因は
  クロスエンコーダ再ランキングを実装していないことと、会話規模がTF-IDFには小さすぎることだと
  考えられる(詳細は`results.md`の3節)。

詳しい分析は `results.md` を参照。
