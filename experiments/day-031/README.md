# Day 031: 「メモリの税(tax)」は実際に起きるか — 自作会話ログでの縮小概念実証

検証対象論文: "Memory Tax: Dissecting the Net Value of Agent Memory"
出典: https://huggingface.co/papers/2610.34073 (arXiv:2610.34073)

著者コードの公開は確認できなかったため、論文の「利益(benefit) vs 税(tax)」という分解の
考え方だけを借りて、自作の小規模な多セッション会話ログで縮小版の概念実証を行った。
追加のAPIキー・GPUは使っていない(Claude Code自身を解答モデルとして使用)。

## 含まれているファイル

- `transcripts/project_nova.md` / `transcripts/trip_planning.md`: 自作の架空の多セッション
  会話ログ(それぞれ3セッション、決定が変化していく+一度しか言及されない具体的事実を含む)
- `questions.md`: 2会話×8問、計16問の質問と正解(gold answer)
- `retrieve.py`: 文字bigram TF-IDFによる素朴な検索スクリプト(RAG条件役、外部ライブラリ不使用)
- `retrieve_output.log`: `retrieve.py` の実行ログ(16問全てのtop-5検索結果)
- `memory/project_nova_memory.md` / `memory/trip_planning_memory.md`: 「現在値は上書き、
  主要な意思決定は変更履歴も保持、付随的な細部は捨てる」という方針で構築した要約メモリ
  (メモリ条件役)
- `answers_and_scoring.md`: 16問全てについて、RAG条件・メモリ条件それぞれの解答過程と採点
- `results.md`: 結果の集計・分析・限界(正直な記録)

## 再現手順

Python 3(標準ライブラリのみ、追加インストール不要)。

```bash
cd experiments/day-031
python3 retrieve.py   # 16問全てについてtop-5検索結果を表示(retrieve_output.logと同じ内容)
```

検索結果が出たら、`memory/*.md` と見比べながら `questions.md` の正解と照らし合わせることで、
`answers_and_scoring.md` の採点を検証できる。

## 結果の要点

- RAG(素朴な検索)条件: 16問中13問正答(81.25%)
- メモリ(要約+変更履歴)条件: 16問中15問正答(93.75%)
- 「税」(RAGは正答、メモリは誤答)が起きたのは1件: ステージングサーバーの機種という、
  計画上の意思決定として扱われなかった付随的な細部を、メモリは圧縮の過程で失っていた。
- 「利益」(メモリは正答、RAGは誤答)が起きたのは3件: いずれも素朴なキーワード検索の
  top-5に、人名や複数セッションに分散した数値が十分に拾われなかったことが原因。
- 今回の縮小実験では、メモリ側の正答率がRAG側を上回った(税1件 < 利益3件)。論文の
  見出しである「メモリは素朴なRAGに負けることが多い」はこの縮小実験では再現しなかった。
  正直にそのまま記録している(詳細と考察は`results.md`の3節・4節)。
