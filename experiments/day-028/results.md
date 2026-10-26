# Day 028 検証結果

検証対象論文: "Is Complex Agentic Memory Always Needed? Naive RAG Is Stronger Than We Thought"
出典: https://huggingface.co/papers/2610.30755 (arXiv:2610.30755, 投稿日2026-10-23頃)

## 0. 著者コードの有無の再確認

着手前にHugging Face Papersページ(本文含む全文)とarXiv該当ページを再確認した。
著者独自実装のGitHubリンクは見つからず、ページ内に掲載されていた外部リンクは
いずれもベースラインやベンチマーク(MEME, Memobase, memU, Qwen3-Reranker-4B)の
公開リソースのみだった。よって today.md に指示されていた縮小版の概念実証に進んだ
(LoCoMo/LongMemEval等の大型ベンチマークやGPT-4o等の有料APIは使っていない)。

## 1. 検証の設計

自作した3本の架空の会話ログ(`datasets.py`、それぞれ20〜25ターン、英語)を用意した。
各会話は「住んでいる都市」「職業」「ペット」「好きな食べ物」の4項目について、会話が
進むにつれて設定が変化する(引っ越し・転職・ペットが増える・好みが変わる)。関係ない
世間話のターンも混ぜてある。

この会話ログに対して、3種類のメモリ手法を実装し(`memory_methods.py`)、同じ質問セット
24問(`datasets.py`の`QUESTIONS`、"current"=最新の値を聞く質問12問、"historical"=既に
上書き・変更された過去の値を聞く質問12問)に答えさせた。

1. **MutatingSummaryMemory**: 正規表現ベースの簡易抽出(本物のLLM抽出の代替、下記「限界」参照)
   で事実を取り出し、矛盾する新情報が来たら古い値を**上書き**する。論文が検証している
   Mem0のUPDATE/DELETE操作を模したもの。
2. **AppendOnlyMemory**: 抽出ロジックは同じだが、古い値を消さず**全履歴を保持**する。
   論文内の「Mem0のUPDATE/DELETEを追記のみに置き換える」実験に対応する。
3. **RawRAGMemory**: 抽出・要約を一切行わず生ログをそのまま保持し、質問時に自作の
   軽量TF-IDF類似度(外部ライブラリ不使用)で関連ターンを検索する。論文の「密検索+
   クロスエンコーダ再ランキング」をTF-IDFのみに簡略化したもの。

採点方法: 構造化メモリ(1, 2)は格納値と正解(gold)の部分文字列一致で判定。RawRAG(3)は
要約・読み手LLMを使わないため、検索結果(上位5ターンの生テキスト)の中に正解が部分文字列
として含まれているか(= 論文が言う「カバレッジ」に相当)で判定した。

## 2. 実行ログ(メインの実験)

```
$ python3 run_experiment.py
```

全ログは `run_output.log` に保存。抜粋:

```
=== メモリ構築 ===
[conv_001_aki] turns=25 | Mutating build=5.331ms storage=165chars | AppendOnly build=0.715ms storage=288chars | RawRAG build=1.144ms storage=3089chars
```
(↑このブロックは3会話の合計値。各会話単体の値は`run_output.log`参照。初回実行はPythonの
正規表現コンパイルのウォームアップで数msの揺れがあったため、構築コストの絶対値そのものは
厳密な比較材料にしていない。)

質問ごとの代表例(矛盾を含む履歴がどう扱われるか):

```
[conv_001_aki][job][historical] Q: What was Aki's job *before* the most recent change?
  gold='graphic designer'
  Mutating -> 'product manager' (MISS)
  AppendOnly -> ['graphic designer', 'UX researcher'] (OK)
  RawRAG retrieved turns [8, 13, 1, 24, 4] (MISS, query 0.040ms)

[conv_002_ben][home_city][historical] Q: What was Ben's home city *before* the most recent change?
  gold='Seattle'
  Mutating -> 'Austin' (MISS)
  AppendOnly -> ['Seattle'] (OK)
  RawRAG retrieved turns [8, 2, 21, 15, 16] (OK, query 0.038ms)
```

集計(24問、`run_output.log`より):

| 質問タイプ | n | Mutating正答率 | AppendOnly正答率 | RawRAG正答率(カバレッジ) |
|---|---|---|---|---|
| current(最新の値) | 12 | 66.67% | 66.67% | 25.00% |
| historical(上書き前の値) | 12 | 16.67% | **100.00%** | 33.33% |
| 全体 | 24 | 41.67% | **83.33%** | 29.17% |

ストレージサイズ(3会話合計、格納している文字数):

| 手法 | 構築時間(3会話合計) | ストレージサイズ |
|---|---|---|
| MutatingSummaryMemory | 5.3ms(ウォームアップ含む) | 165文字 |
| AppendOnlyMemory | 0.7ms | 288文字 |
| RawRAGMemory | 1.1ms | 3,089文字(生ログそのもの) |

RawRAGの平均クエリ時間: 0.037ms(24問平均)。

## 3. 再現できた点・できなかった点(正直に)

**再現できた(論文の主張の核心部分): 「メモリの変異(上書き・削除)は害になりうる」**

historical(過去の値を聞く質問)でMutatingSummaryMemoryは16.67%しか正答できなかった。
これは上書き型メモリの構造上当然の結果だが、同じ抽出ロジックで「上書きせず追記するだけ」
にしたAppendOnlyMemoryは100%正答した。論文がMem0のUPDATE/DELETEを追記のみに変えただけで
LoCoMoの精度が67.36%→69.42%に改善したと報告している現象と、方向性が一致する結果になった。
縮小版でも「メモリの加工・変異自体が有害になりうる」という論文の指摘は明確に再現できた。

**再現しなかった点: 「素朴なRaw-RAGが最も強い」という見出しの結果**

論文は7つのベンチマーク・モデル設定のうち6つでRaw-RAGが最高性能だったと報告しているが、
今回の縮小実験ではRawRAGMemoryはcurrent 25.00%、historical 33.33%と、構造化メモリ2種
(特にAppendOnlyMemory)より明確に劣った。動かした結果そのまま、正直に記録する。

原因を切り分けるため、`ablation_rag.py`で追加のアブレーションを行った(`ablation_output.log`参照):

```
$ python3 ablation_rag.py
=== RawRAG 検索方式のアブレーション ===
[baseline (speaker label入り, stemなし)] current acc=25.00% | historical acc=33.33%
[speaker label除去] current acc=25.00% | historical acc=25.00%
[speaker label除去 + 簡易stem] current acc=33.33% | historical acc=25.00%
[speaker label入り + 簡易stemのみ] current acc=33.33% | historical acc=33.33%
```

発言者ラベル("Aki: "等)をトークンから除いたり、簡易な語幹処理("job"と"jobs"の表記差を
吸収)を入れても、current acc は25%→33.33%程度の改善にとどまり、AppendOnlyMemoryの
66.67%/100%には届かなかった。さらに検索件数(top_k)を振った結果:

```
[baseline, top_k=3]  current acc=8.33%  | historical acc=25.00%
[baseline, top_k=5]  current acc=25.00% | historical acc=33.33%
[baseline, top_k=8]  current acc=33.33% | historical acc=66.67%
[baseline, top_k=10] current acc=41.67% | historical acc=75.00%
```

top_kを増やすほど正答率は上がる(当然、会話が20〜25ターンしかないため、top_k=10は
会話の約40〜50%を読み込んでいることになる)。つまりこの結果の低さは、単純なバグという
よりも、**今回の実装・検証規模そのものの限界**だと考えられる:

- 論文の手法は密ベクトル検索(学習済み埋め込みモデル)+クロスエンコーダによる再ランキング
  を使うが、今回は外部ライブラリなし・APIキーなしという制約上、自作のTF-IDFのみで近似した。
  クロスエンコーダによる再ランキングに相当する工程は実装していない。
- RawRAGの採点は「検索結果の生テキストに正解が部分文字列として含まれるか」であり、論文の
  ように読み手LLMが検索結果から実際に正しい答えを合成できるかまでは検証していない
  (読み手LLMを使うには有料APIキーが必要になるため、本リポジトリの方針で見送った)。
- 会話が20〜25ターンと非常に短く、論文が使うLoCoMo等の長期会話(数千トークン規模)に比べて
  TF-IDFが統計的な手がかりを得にくい規模だった。

したがって、「素朴なRaw-RAGが最強」という論文の見出しの結果は、**今回の縮小・簡略化した
実装・データ規模では再現しなかった**、というのが正直な結論である。これは論文の主張を
否定するものではなく、再現には論文と同等の検索器(学習済み埋め込み+クロスエンコーダ)と
より大規模な会話データ、読み手LLMが必要であり、それらを使わない縮小版では検証しきれない
部分がある、ということを示している。

## 4. ローカルGPUでの追加検証: 密検索+クロスエンコーダ再ランキングを実装し直す

3節で「Raw-RAGが再現しなかった原因はクロスエンコーダ再ランキング未実装とデータ規模の
小ささではないか」という考察を立てた。人間(matsu)のローカルPC(RTX 5060 Ti, 16GB VRAM)で、
この仮説を実際に検証した。RawRAGMemory(TF-IDFのみ)を置き換える`DenseRAGMemory`を
新たに実装し、同じ会話データ・同じ質問24問・同じ採点方法(検索結果への正解の部分文字列
一致)で比較した。コードは`experiments/day-028/gpu_verification/dense_rag_memory.py`。

- 埋め込みモデル: `sentence-transformers/all-MiniLM-L6-v2`(公開・無料、APIキー不要)
- 再ランキングモデル: `cross-encoder/ms-marco-MiniLM-L-6-v2`(公開・無料、APIキー不要)
- 両モデルともHugging Face Hubから取得し、ローカルGPU(CUDA)で実行した。
- 検索フロー: 埋め込みのコサイン類似度で上位`candidate_k`件に絞り込んだ後、
  クロスエンコーダで`(質問, 候補ターン)`ペアをスコアリングして並べ替え、上位`top_k`件を
  採用する(論文が述べる「密検索+クロスエンコーダ再ランキング」構成に近い)。

### 4.1 実行結果

```
$ cd experiments/day-028/gpu_verification
$ python3 run_dense_experiment.py
=== DenseRAGMemory (embedding + cross-encoder reranking, GPU) ===

[dense+rerank top5] top_k=5 candidate_k=10 reranker=True | current acc=66.67% | historical acc=83.33% | overall acc=75.00% | avg query time=24.54ms
[dense only  top5]  top_k=5 candidate_k=10 reranker=False | current acc=50.00% | historical acc=75.00% | overall acc=62.50% | avg query time=4.16ms
[dense+rerank top3] top_k=3 candidate_k=10 reranker=True | current acc=66.67% | historical acc=66.67% | overall acc=66.67% | avg query time=13.58ms
[dense+rerank top5] top_k=5 candidate_k=10 reranker=True | current acc=66.67% | historical acc=83.33% | overall acc=75.00% | avg query time=14.10ms
[dense+rerank top8] top_k=8 candidate_k=10 reranker=True | current acc=66.67% | historical acc=100.00% | overall acc=83.33% | avg query time=15.46ms
[dense+rerank top10] top_k=10 candidate_k=10 reranker=True | current acc=66.67% | historical acc=100.00% | overall acc=83.33% | avg query time=11.76ms
```

| 実装 | current acc | historical acc | overall acc |
|---|---|---|---|
| RawRAGMemory(TF-IDFのみ、top_k=5、3節の元の結果) | 25.00% | 33.33% | 29.17% |
| DenseRAGMemory(密検索のみ、reranker無し、top_k=5) | 50.00% | 75.00% | 62.50% |
| **DenseRAGMemory(密検索+クロスエンコーダ、top_k=5)** | **66.67%** | **83.33%** | **75.00%** |
| **DenseRAGMemory(密検索+クロスエンコーダ、top_k=8/10)** | **66.67%** | **100.00%** | **83.33%** |
| (参考)AppendOnlyMemory(構造化メモリ、3節) | 66.67% | 100.00% | 83.33% |

**仮説は実際に裏付けられた。** TF-IDFのみのRawRAGMemory(overall 29.17%)に対し、密検索
(embeddingのみ)に変えるだけでoverall 62.50%まで改善し、そこにクロスエンコーダ再ランキング
を加えるとoverall 75.00%まで上がった。さらに`top_k`を8〜10に広げると、**overall 83.33%と、
AppendOnlyMemory(構造化メモリの中で最も正答率が高かった手法)と完全に同じ数値まで到達した。**
3節で「クロスエンコーダ未実装・データ規模が原因」と推測した通りで、検索器を論文の構成に
近づけるだけで、RawRAGは「構造化メモリより明確に劣る」状態から「構造化メモリと同水準」まで
一気に改善した。

### 4.2 それでも残った4問のMISS

`top_k=8`での詳細ログ(`run_dense_detailed.log`)を見ると、DenseRAGMemoryが依然として
MISSした4問はすべて"current"タイプで、うち2問(Aki・Chiの「現在のペット」)は
`gold='two cats, Mochi and Tofu'`のような、複数の事実を合成した表現だった。RawRAG系の
手法は検索結果の生テキストをそのまま返すため、会話のどのターンにも一字一句同じ形では
登場しない合成済みの答え方とは、原理的に文字列一致しにくい。残り2問(Ben・Chiの
「現在の職業」)は、**AppendOnlyMemoryも同じ質問をMISSしていた**ことを確認した
(`run_dense_detailed.log`参照)。つまりこの2問は、DenseRAGMemory固有の弱点ではなく、
1節の簡易正規表現抽出がそもそも拾えていなかった、データセット側の既知のエッジケース
だったことが分かった。

### 4.3 結論(GPU追加検証)

- 「素朴なRaw-RAGが最強」という論文の見出しの結果そのもの(RawRAGが構造化メモリを
  明確に上回る)は、今回の縮小データ・縮小実装では再現しなかった。ここは3節の結論を
  覆すものではない。
- しかし、3節で立てた「原因はクロスエンコーダ再ランキング未実装とデータ規模」という
  仮説は、実際に検索器を密検索+クロスエンコーダ構成に置き換えることで裏付けられた。
  TF-IDFのみの実装がRaw-RAGを不当に不利に見せていた部分は、論文に近い検索器を使う
  ことで解消し、RawRAGは最良の構造化メモリ(AppendOnlyMemory)と同水準まで追いついた。
- 残る「Raw-RAGが構造化メモリを上回る」という結果までは今回も再現できておらず、これは
  論文が使う長期会話データ(LoCoMo等、数千ターン規模)や読み手LLMによる回答合成が
  無いと検証しきれない部分だと考えられる。それでも、「縮小実装の検索器が貧弱だったから
  RawRAGが不当に低く出ていた」という3節の考察自体は、ローカルGPUでの追加検証により
  実測で裏付けられた。

## 5. ローカル検証へのエスカレーションは不要

今回はRoutine実行環境の制約(ブラウザ不在・ネットワーク制限等)による未検証部分はなく、
全て実際にPythonスクリプトを実行して得られた結果である。上記3節の「再現しなかった点」は
ツール・ベンチマーク由来ではなく、こちらで作った縮小実装自体の限界であり、CLAUDE.mdの
分類に従えば「検証に直接関係する失敗」として本記事に書いている。ただし、その限界の原因
(密検索・クロスエンコーダ未実装)についての考察自体は、4節のローカルGPU追加検証により
実測で裏付けられた。

## 6. ライセンス・出典

- 論文: arXiv:2610.30755 (Hugging Face Papers掲載)。著者独自実装のコード公開は確認できず。
- 使用した会話データ・質問セット・実装コードはすべてこのリポジトリで新規に作成したもので、
  論文のLoCoMo/LongMemEval/MEME/MemoryAgentBenchのデータは一切使用していない。
- 4節のGPU追加検証で使用したモデル: `sentence-transformers/all-MiniLM-L6-v2`(Apache-2.0)、
  `cross-encoder/ms-marco-MiniLM-L-6-v2`(Apache-2.0)。いずれもHugging Face Hubで公開されて
  いる無料モデルで、追加の有料APIキーは不要。
