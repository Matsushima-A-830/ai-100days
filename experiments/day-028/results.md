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

## 4. ローカル検証へのエスカレーションは不要

今回はRoutine実行環境の制約(ブラウザ不在・ネットワーク制限等)による未検証部分はなく、
全て実際にPythonスクリプトを実行して得られた結果である。上記3節の「再現しなかった点」は
ツール・ベンチマーク由来ではなく、こちらで作った縮小実装自体の限界であり、CLAUDE.mdの
分類に従えば「検証に直接関係する失敗」として本記事に書いている。

## 5. ライセンス・出典

- 論文: arXiv:2610.30755 (Hugging Face Papers掲載)。著者独自実装のコード公開は確認できず。
- 使用した会話データ・質問セット・実装コードはすべてこのリポジトリで新規に作成したもので、
  論文のLoCoMo/LongMemEval/MEME/MemoryAgentBenchのデータは一切使用していない。
