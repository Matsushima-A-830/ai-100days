---
title: "検索ネイティブ事前学習のQueryLM(360M)を8問から300問に広げたら、「検索が裏目」は消えて正解が1問から17問に増えた"
emoji: "🔍"
type: "tech"
topics: ["ai", "llm", "nlp", "huggingface", "python"]
published: false
---

## これは何を試した記事か

事後学習(SFTやRL)の段階で検索ツールを使わせる手法はよく見るが、事前学習の段階からモデル自身に検索クエリを発行させ、取得した証拠を使わせる「search-native」な学習を提案した論文 [Search From the Start: Search-Native Pretraining for Language Models](https://arxiv.org/abs/2611.26809)(EPFL / University of Toronto、Ponkshe・Je・Taga・Raffel・Jaggi)が、学習済みチェックポイントを[Apache-2.0で公開している](https://huggingface.co/collections/Kausp11/search-native-pretraining)。

筆者はこれを実際にダウンロードして動かし、同じアーキテクチャ・同じ計算量で学習された「検索ブロックあり(QueryLM)」と「検索ブロックなし(Standard)」の360Mモデルを比べた。
最初は8問の知識QAで比べ、「検索を使わなくてもQueryLMが勝つが、検索させると正解が減る」という結果に見えた。
ところが、手元のPCでGPU・CPU、BF16・FP32を変えて同じ8問を再実行し、さらにNatural Questionsの300問に広げると、結論はほぼ逆になった。
この記事は、その経緯をそのまま書いたものだ。

- 出典: 論文 https://arxiv.org/abs/2611.26809 / モデル https://huggingface.co/collections/Kausp11/search-native-pretraining (Apache-2.0) / プロジェクトページ https://kaustubhp11.github.io/querylm
- 検証したモデル: `Kausp11/querylm-wiki-360m`、`Kausp11/standard-wiki-360m`、`Kausp11/querylm-wiki-360m-sft-search`(いずれも361.8Mパラメータ、BF16)

## QueryLMとは何か

QueryLMは、事前学習のテキストの中に「ここで検索すると予測しやすくなる」位置があらかじめ注釈され、`<WEB_QUERY>クエリ</WEB_QUERY> <WEB_RESPONSE>取得した文章</WEB_RESPONSE>`という検索ブロックが挿入された状態で学習されたモデルだ。
注釈はGemma 4 E4B-itにLoRAを当てたアノテータモデルが付け、取得文章はSphereコーパスへのBM25検索から来ている。
学習時の損失は本文とクエリ・タグにだけかかり、取得された文章自体やその終了タグには損失がかからない。
つまりモデルは「レスポンス(取得文章)を予測する」ことを学習しておらず、「有効な場所でクエリを書く」ことと「渡された文章を使って続きを書く」ことを学習している。
取得文章は呼び出し側(今回は筆者)が用意する前提になっている。

ペアとなる`Kausp11/standard-wiki-360m`は、同じアーキテクチャ・同じ計算量で、検索ブロックを含まないプレーンなWikipediaテキストだけを学習したベースラインだ。
論文はこの2つを比べることで「検索ネイティブな事前学習そのものが何を変えるか」を測っている。

## 環境

| 項目 | 内容 |
|---|---|
| 最初の実行 | CPU推論、torch 2.15.0、transformers 5.24.0、Python 3.11.18 |
| 手元のPC | WSL2 (Ubuntu)、NVIDIA GeForce RTX 5060 Ti 16GB、torch 2.15.0+cu132、transformers 5.24.0、Python 3.14.7 |
| モデル取得 | Hugging Face Hubから直接ダウンロード(認証不要、合計約2.1GB) |

## まずモデルカードの使用例をそのまま動かす

モデルカード記載のサンプルコードを一字一句そのまま実行した。

```python
query = generate(prompt + "<WEB_QUERY>", max_new_tokens=24, stop_id=Q_CLOSE).strip()
block = f"<WEB_QUERY>{query}</WEB_QUERY> <WEB_RESPONSE>{my_search(query)}</WEB_RESPONSE>"
answer = generate(prompt + block + "\nAnswer:", max_new_tokens=16, allow_search=False)
```

```
$ .venv/bin/python 01_reproduce_cards.py
=== QueryLM (search-native) ===
WEB_QUERY ids: 49152 49153
query : Jane Austen Pride and Prejudice capital Australia answer
answer: The capital of Australia

=== Standard (no-search baseline) ===
answer: Gold
```

出力はモデルカードに記載された文字列と一致した。
手元のPCでも、CPU(BF16・FP32)とGPU(FP32)では同じ出力だった。
GPUのBF16だけは、Standardの答えが`Gold`ではなく`Australia`になった。
greedy decodingでも、計算する機器と精度が変わると出力が変わりうる、という点はこの後の話にも関わってくる。

## 8問の知識QAで3条件を比較する

次に、8つの知識QA(作者・元素記号・首都・画家・年号・山・人物)を、3つの条件で比較した。
いずれもgreedy decoding(`do_sample=False`)で、モデルカードと同じ2問のfew-shot例(Pride and Prejudiceの作者、金の元素記号)を前に付けている。

- **(A) QueryLM・検索なし**: `<WEB_QUERY>`トークンを`bad_words_ids`で禁止し、検索を使わせない。
- **(B) QueryLM・検索あり**: モデル自身に検索クエリを書かせ、各問に対応する正しい参考パッセージ(Wikipedia由来の事実の一文)を`<WEB_RESPONSE>`として渡し、続きを生成させる。
- **(C) Standard**: 検索ブロックを学習していないベースラインに、検索なしで同じ問いを出す。

最初の実行(CPU・BF16)の結果がこれだ。

| 質問 | 正解 | (A) 検索なし | (B) 検索あり | (C) Standard |
|---|---|---|---|---|
| Pride and Prejudiceの作者は? | Jane Austen | Jane Austen ✅ | (空文字列) ❌ | Jane Austen ✅ |
| 金の元素記号は? | Au | Au ✅ | Au ✅ | Gold? ❌ |
| オーストラリアの首都は? | Canberra | The capital of Australia ❌ | The capital of Australia ❌ | Gold ❌ |
| モンゴルの首都は? | Ulaanbaatar | The capital of Mongolia? ❌ | Ulaanbaatar ✅ | Gold ❌ |
| モナリザを描いたのは? | Leonardo da Vinci | Jane Austen ❌ | The Mona Lisa ❌ | The Mona Lisa? ❌ |
| ベルリンの壁崩壊は何年? | 1989 | 1949 ❌ | The Berlin Wall fell? ❌ | 1961 ❌ |
| 世界最高峰は? | Mount Everest | Mount Everest ✅ | Au ❌ | The highest mountain in the world? ❌ |
| 月に最初に降りたのは誰? | Neil Armstrong | John Lennon ❌ | (空文字列) ❌ | The first person to walk on the Moon? ❌ |
| **正解数** | | **3/8** | **2/8** | **1/8** |

一見すると「検索なしでもQueryLMはStandardに勝ち、検索させると正解が減る」と読める。
Pride and Prejudiceと世界最高峰は、検索前は正解していたのに、検索ブロックを挟んだ途端に空文字列や`Au`に変わった。

## 手元のPCで同じ8問を再実行すると、数字が変わった

この結果を手元のPCで確かめた。
スクリプトは変えずに、モデルを載せるデバイスとdtypeだけを差し替えるラッパー`run_device.py`を書き、CPU/GPU × BF16/FP32の4条件で実行した。
ラッパーを通したCPU・BF16の結果が、ラッパーなしの実行と完全に一致することも確認している。

```
$ .venv/bin/python run_device.py 02_qa_compare.py cuda bf16
[run_device] script=02_qa_compare.py device=cuda dtype=bf16 torch=2.15.0+cu132 transformers=5.24.0 gpu=NVIDIA GeForce RTX 5060 Ti
$ python grade_devices.py PR=. cpu-bf16=device_runs/cpu-bf16 cuda-bf16=device_runs/cuda-bf16 cpu-fp32=device_runs/cpu-fp32 cuda-fp32=device_runs/cuda-fp32
| run | (A) QueryLM no search | (B) QueryLM search | (C) Standard | (D) sft-search |
|---|---|---|---|---|
| PR | 3/8 | 2/8 | 1/8 | 8/8 |
| cpu-bf16 | 3/8 | 3/8 | 1/8 | 8/8 |
| cuda-bf16 | 3/8 | 3/8 | 1/8 | 8/8 |
| cpu-fp32 | 3/8 | 3/8 | 1/8 | 8/8 |
| cuda-fp32 | 3/8 | 3/8 | 1/8 | 8/8 |
```

(`PR`の行が最初の実行。)

手元の4条件では、(B)はすべて3/8で、(A)と同じだった。
違いはモナリザの1問だけで、最初の実行ではクエリ`Jane Austen Mona Lisa painting question`から`The Mona Lisa`と答えていたのが、手元ではすべて`Au Mona Lisa painting artist name`というクエリから`Leonardo da Vinci`と正しく答えた。
FP32ではCPUでもGPUでも同じ出力なので、最初の実行の値は、その環境でのBF16の小さな数値差がgreedy decodingの分岐を変えたものだと考えている。

もう1つ気づいたことがある。
8問のうちPride and Prejudiceと金の元素記号の2問は、few-shot例とまったく同じ問題で、答えがプロンプトに書かれている。
これを除いた6問では、(A)は1問(世界最高峰)、(B)は2問、(C)は0問しか正解していない。
1問の違いで「検索が裏目に出た」かどうかが入れ替わる大きさの標本で、結論を出すのは無理があった。

## Natural Questionsの300問に広げる

そこで、プロンプト・few-shot・decodingは同じまま、Natural Questionsの開発セットに広げた(`04_nq_scale.py`)。
データは`Tevatron/wikipedia-nq`の`nq-dev.jsonl.gz`(DPR形式)で、ファイル先頭から、正解を含むWikipedia段落(約100語)が付いている質問を300問使った。
検索条件では、モデルがどんなクエリを書いても、この正解入りの段落を`<WEB_RESPONSE>`として渡す。
常に正しい文書が返ってくる理想的なretrieverで、「良い検索結果を渡されたときに使えるか」を測っている。
採点は、正規化(小文字化・句読点と冠詞の除去)した回答の1行目(sft-search版は1文目)に正解文字列が含まれるかどうかで、部分一致なのでやや甘い。
チャット微調整版(sft-search)については、検索トークンを禁止した条件(D0)も足した。

```
$ .venv/bin/python 04_nq_scale.py 300 cpu bf16 nq_scale_results.jsonl
[04] n=300 device=cpu dtype=bf16 torch=2.15.0+cu132
[04] done in 3196s
$ python summarize_nq.py
| condition | correct | accuracy | 95% CI |
|---|---|---|---|
| (A) QueryLM, no search | 1/300 | 0.3% | 0.1-1.9% |
| (B) QueryLM, own query + gold passage | 17/300 | 5.7% | 3.6-8.9% |
| (C) Standard, no search | 1/300 | 0.3% | 0.1-1.9% |
| (D0) sft-search, no search | 3/300 | 1.0% | 0.3-2.9% |
| (D) sft-search, own query + gold passage | 80/300 | 26.7% | 22.0-31.9% |

QueryLM vs Standard (no search): only A correct = 1, only C correct = 1, McNemar exact p = 1
QueryLM: no search -> search: only A correct = 1, only B correct = 17, McNemar exact p = 0.000145
sft-search: no search -> search: only D0 correct = 0, only D correct = 77, McNemar exact p = 1.32e-23
```

8問の再実行でCPUとGPUの出力が同じだったため、300問はCPU・BF16で実行した(3196秒)。

### 分かったこと(1): 検索なしでは、QueryLMとStandardに差はなかった

検索を使わない条件では、QueryLMもStandardも300問中1問しか正解しなかった。
8問での「3対1」の差は、few-shot例と同じ2問と世界最高峰の1問から来ていたことになる。
NQのような一般的な質問は、360Mのベースモデルにはほぼ答えられない。
論文は別の評価設定で差を報告しているので、これは「論文が間違っている」という話ではなく、この最小サイズ・この問い方では差が見えなかった、という観察だ。

### 分かったこと(2): 正しい段落を渡すと、正解は1問から17問に増えた

QueryLMに正解入りの段落を渡すと、正解は1問から17問に増えた。
検索で正解が崩れたのは300問中1問だけだった(ロンドンの水道水の水源を聞いた問いで、検索なしでは`The water in the bath is from the river Thames.`と答えていたのが、検索ありでは質問文をそのまま返した)。
8問で見えた「検索が裏目に出る」現象は実際に起きるが、全体としては検索ははっきりプラスに働いている。

### 分かったこと(3): ベースモデルのクエリはfew-shot例に引きずられる

QueryLMのベースモデルが書いたクエリは、300件中235件にfew-shot例の単語(Jane Austen、Pride and Prejudice、Au、gold)が混ざっていた。

```json
{
  "question": "Who was the last person executed in ireland?",
  "B_query": "Jane Austen last person executed ireland answer",
  "B": "Michael Manning"
}
```

それでも、渡す段落が正しければ答えられることがある(この例は正解)。
一方で、回答そのものも`What is the chemical symbol for gold?`(43件)のように例題を復唱するものが多かった。
小さなベースモデルは、目の前の質問よりも、直前に見せた例の形に強く引っ張られる。

### 分かったこと(4): チャット微調整版は段落をよく使うが、それでも3割弱

sft-search版は、検索なしでは3/300だったのが、段落を渡すと80/300(26.7%)まで上がった。
クエリにfew-shotの単語が混ざることもほとんどなかった(1/300)。
ただし、8問のときの「8/8」から受ける印象よりはずっと低く、段落に答えがあっても別の内容を書き続けたり、余計な説明を足したりする問題が7割以上あった。

```json
{
  "question": "Who introduced the system of civil services in india?",
  "D_query": "India civil services system introduction year",
  "D": "The civil services in India are a system of civil services that was introduced in India in 1947. ..."
}
```

8問のときにも、本題は正しいのに余談で幻覚を足す例があった。
モナリザの問いでは「ダ・ヴィンチはティエポロの弟子だった」という誤りを書き、これは手元の4条件すべてで出た。
エベレストの問いで「インドの州にある」と書いた誤りは、BF16では出たがFP32では出なかった。

## まとめ

- モデルカードの使用例は、公開された重みでそのまま再現できた(GPUのBF16だけStandardの出力が変わった)。
- 8問で見えた「検索させると3/8→2/8に下がる」は、手元のCPU/GPU × BF16/FP32の4条件では再現せず、すべて3/8だった。差は1問で、最初の実行環境でのBF16の数値差によるものと考えている。8問中2問はfew-shot例と同じ問題でもあった。
- Natural Questions 300問では、検索なしのQueryLMとStandardはどちらも1/300で差がなかった。
- 正解入りの段落を渡すと、QueryLMは1/300→17/300、チャット微調整版は3/300→80/300に上がった。検索で正解が崩れたのは300問中1問だけだった。
- 小さな標本と1回の実行で「意外な結果」が出たときは、まず精度や機器を変えて再実行し、問題数を増やして確かめるべきだった、というのが今回いちばんの学びだった。
- モデルカードには「Not a product」「research artifact」と明記されている。360Mクラスでは、チャット微調整版でも正しい段落を渡して3割弱しか答えられず、実用品質にはまだ遠い。

## ライセンスと再現性について

モデル重みはApache-2.0で公開されている。
事前学習テキストは英語Wikipedia(CC BY-SA 4.0)で、学習中にマスク済みコンテキストとして使われた検索パッセージの出典Sphere(CC BY-NC 4.0)は、モデルリポジトリには含まれていない。
sft-search版のモデルカードには、微調整データの選別にLlama 3.1 8Bを使い、Llama 3.1で生成された会話を含むため、「Built with Llama」とLlama 3.1 Community Licenseの表示がある。
評価に使ったNatural Questionsの質問はCC BY-SA 3.0で、段落は英語Wikipediaのものだ。
検証コード・ログ・全生成結果は`experiments/day-057/`に置いてある。
8問の検索ステップでは、ライブのWeb検索APIを呼ぶのではなく、モデルカード自身のデモと同じ「固定文字列を返す」方式(ただし筆者が各問に対応する正しい事実の一文を用意したもの)を使い、300問ではDPRの正解入り段落を渡した。
論文自体の検索インデックス(BM25 over Sphere)の再現はスコープ外とした。
