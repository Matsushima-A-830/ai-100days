---
title: "検索ネイティブ事前学習のQueryLM(360M)は検索を使わなくても同条件ベースラインに3対0で勝ったが、検索を使わせると裏目に出ることもあった"
emoji: "🔍"
type: "tech"
topics: ["ai", "llm", "nlp", "huggingface", "python"]
published: false
---

## これは何を試した記事か

事後学習(SFTやRL)の段階で検索ツールを使わせる手法はよく見るが、事前学習の段階からモデル自身に検索クエリを発行させ、取得した証拠を使わせる「search-native」な学習を提案した論文 [Search From the Start: Search-Native Pretraining for Language Models](https://arxiv.org/abs/2611.26809)(EPFL / University of Toronto、Ponkshe・Je・Taga・Raffel・Jaggi)が、学習済みチェックポイントを[Apache-2.0で公開している](https://huggingface.co/collections/Kausp11/search-native-pretraining)。

筆者はこれを実際にダウンロードして動かし、同じアーキテクチャ・同じ計算量で学習された「検索ブロックあり(QueryLM)」と「検索ブロックなし(Standard)」の360Mモデルを、同じ8問の知識QAで比較した。
さらに、QueryLMをチャット形式で微調整した版(`querylm-wiki-360m-sft-search`)も同じ問いで試した。

- 出典: 論文 https://arxiv.org/abs/2611.26809 / モデル https://huggingface.co/collections/Kausp11/search-native-pretraining (Apache-2.0) / プロジェクトページ https://kaustubhp11.github.io/querylm
- 検証したモデル: `Kausp11/querylm-wiki-360m`、`Kausp11/standard-wiki-360m`、`Kausp11/querylm-wiki-360m-sft-search`(いずれも361.8Mパラメータ、BF16)

## QueryLMとは何か

QueryLMは、事前学習のテキストの中に「ここで検索すると予測しやすくなる」位置があらかじめ注釈され、`<WEB_QUERY>クエリ</WEB_QUERY> <WEB_RESPONSE>取得した文章</WEB_RESPONSE>`という検索ブロックが挿入された状態で学習されたモデルだ。
注釈はGemma 4 E4B-itにLoRAを当てたアノテータモデルが付け、取得文章はSphereコーパスへのBM25検索から来ている。
学習時の損失は本文とクエリ・タグにだけかかり、取得された文章自体やその終了タグには損失がかからない。
つまりモデルは「レスポンス(取得文章)を予測する」ことを学習しておらず、「有効な場所でクエリを書く」ことだけを学習している。
取得文章は呼び出し側(今回は筆者)が用意する前提になっている。

ペアとなる`Kausp11/standard-wiki-360m`は、同じアーキテクチャ・同じ計算量で、検索ブロックを含まないプレーンなWikipediaテキストだけを学習したベースラインだ。
QueryLMは検索ブロックを挟む分、1シーケンスあたりのテキスト量が減るので、Standardはその分プレーンテキストを多く学習している。
論文はこの2つを比べることで「検索ネイティブな事前学習そのものが何を変えるか」を測っている。

## 環境

| 項目 | 内容 |
|---|---|
| 実行環境 | CPU推論のみ(GPU不要) |
| ライブラリ | torch 2.15.0(CPU版)、transformers 5.24.0、Python 3.11.18 |
| モデル取得 | Hugging Face Hubから直接ダウンロード(認証不要、合計約2.1GB) |

モデルカードに明記されている通り、361.8MパラメータというサイズはCPUでも数秒で推論できる。
GPUや有料APIキーは一切使っていない。

## まずモデルカードの使用例をそのまま動かす

いきなり自分の条件で試す前に、モデルカード記載のサンプルコードを一字一句そのまま実行した。

```python
query = generate(prompt + "<WEB_QUERY>", max_new_tokens=24, stop_id=Q_CLOSE).strip()
block = f"<WEB_QUERY>{query}</WEB_QUERY> <WEB_RESPONSE>{my_search(query)}</WEB_RESPONSE>"
answer = generate(prompt + block + "\nAnswer:", max_new_tokens=16, allow_search=False)
```

```
=== QueryLM (search-native) ===
query : Jane Austen Pride and Prejudice capital Australia answer
answer: The capital of Australia

=== Standard (no-search baseline) ===
answer: Gold
```

出力はモデルカードに記載された文字列と完全に一致した。
公開されている重みは、カードの説明通りにそのまま動く。

## 8問の知識QAで3条件を比較する

次に、モデルカードの例より広げて、8つの知識QA(作者・元素記号・首都・画家・年号・山・人物)を、3つの条件で比較した。
いずれもgreedy decoding(`do_sample=False`)で、ランダム性はない。

- **(A) QueryLM・検索なし**: `<WEB_QUERY>`トークンを`bad_words_ids`で禁止し、検索を使わせない。Standardと同じ情報量で比較する条件。
- **(B) QueryLM・検索あり**: モデル自身に検索クエリを書かせ、各問に対応する正しい参考パッセージ(Wikipedia由来の事実)を`<WEB_RESPONSE>`として渡し、続きを生成させる。
- **(C) Standard**: 検索ブロックを学習していないベースラインに、検索なしで同じ問いを出す。

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
| **正解数** | | **3/8** | **2/8** | **0/8** |

実行コマンドと生ログ:

```bash
.venv/bin/python 02_qa_compare.py
```

```json
{
  "question": "What is the capital of Mongolia?",
  "querylm_no_search": "The capital of Mongolia?",
  "querylm_query": "Mongolia capital symbol gold Au",
  "querylm_retrieved": "Ulaanbaatar is the capital and largest city of Mongolia.",
  "querylm_with_search": "Ulaanbaatar",
  "standard": "Gold"
}
```

(全8問の完全なログはリポジトリの`experiments/day-057/qa_results.json`に記録している。)

### 分かったこと(1): 検索を使わなくても、QueryLMはStandardより強い

検索を一切使わせていない(A)の条件でも、QueryLMは3/8正解しているのに対し、Standardは0/8だった。
同じアーキテクチャ・同じ計算量で、学習テキストに検索ブロックを混ぜて事前学習しただけで、素の知識定着量に差が出ている。
これは論文の主張(同FLOPsでQueryLMがStandardベースラインを上回る)の方向性と一致する、360Mという最小サイズでの定性的な観察だ。
Standardは「Gold?」「The Mona Lisa?」のように、質問文をそのまま疑問形で返すパターンが目立ち、Q&A形式そのものの維持にも苦労していた。

### 分かったこと(2): ベースモデルに検索を使わせても、安定して賢くなるわけではない

次に意外だったのが、QueryLMに実際に検索をさせた(B)の結果だ。
モンゴルの首都では検索が有効に働き、(A)では非回答だったのが(B)では「Ulaanbaatar」と正しく答えられるようになった。
しかし、Pride and Prejudiceの作者と世界最高峰では逆に、検索前には正解していたのに検索ブロックを挟んだ途端、空文字列や「Au」という無関係な単語に変わってしまった。
正解数で見ても(A)の3/8より(B)は2/8と少ない。

生成されたクエリ自体も、文脈が混線している跡が見える。
世界最高峰を聞いているのに、QueryLMが書いたクエリは「tallest mountain world answer **Au symbol**」で、直前に出した金の元素記号の問題の単語が残っていた。
360Mという極小サイズでは、少数の例を見せただけでは文脈の切り替えが安定しないようだ。
ベースモデル(チャット微調整なし)は「検索結果を使って答えを言い直す」という形式自体が不安定で、たまたま上手くいく場合と裏目に出る場合が混在している、というのが正直な評価になる。

### 分かったこと(3): チャット微調整版では、検索の活用がはっきり安定する

同じ8問を、QueryLMをチャット形式・検索込みの対話データで1エポック微調整した`querylm-wiki-360m-sft-search`で試すと、結果が一変した。

```bash
.venv/bin/python 03_sft_variant.py
```

```json
{
  "question": "What is the tallest mountain in the world?",
  "query": "tallest mountain world tallest mountain name",
  "answer": "The tallest mountain in the world is Mount Everest, located in the Himalayas, at an elevation of  above sea level. The mountain is  tall, and is the highest point in the world. It is located in the Indian state of Himachal Pradesh, and is the highest point in the state of Himachal..."
}
```

8問すべてで、本題の答えは正しく、渡した参考パッセージの中核事実を正確に取り込めていた。
ベースモデルで見られた「検索したのに空文字列や無関係な単語になる」という不安定さは、チャット微調整後には一度も見られなかった。

ただし、幻覚が完全に消えたわけではない。
上の例では、エベレストの標高の数値が欠落している(テンプレートの変数が埋まっていないような出方をしている)うえ、「located in the Indian state of Himachal Pradesh」という一文を付け足している。
実際のエベレストはインドの州ではなく、ネパールと中国(チベット)の境にある。
モナリザの画家を聞いた問いでも、本題(レオナルド・ダ・ヴィンチ)は正しいが、「He was a pupil of the painter and architect, Giovanni Battista Tiepolo」という、事実と異なる師弟関係を付け加えていた。
渡した情報の中核は正確に使えるようになった一方、そこから先の「補足」は検証対象ではなく、モデル自身の(誤った)事前学習知識から生成されている。

## まとめ

- 検索ネイティブな事前学習(QueryLM)は、検索を使わなくても同条件のStandardベースラインより知識QAに強い、という方向性は360Mという最小サイズでも定性的に確認できた(3/8 vs 0/8)。
- しかしベースモデルのまま検索を使わせても、安定して賢くなるわけではなく、むしろ既知の正解を崩すケースがあった(3/8→2/8)。「検索機能を安定して使いこなす」にはチャット微調整が重要に見える。
- チャット微調整版(sft-search)は、渡された事実の中核部分を8問すべてで正確に使えたが、それでも補足部分には幻覚が残っていた(エベレストの所在地、ダ・ヴィンチの師弟関係など)。
- モデルカードには「Not a product」「research artifact」と明記されている。360Mクラスでは、検索ネイティブ事前学習という手法自体の効きは見えるものの、実用品質にはまだ遠いという印象だった。

## ライセンスと再現性について

モデル重みはApache-2.0で公開されている。
事前学習テキストは英語Wikipedia(CC BY-SA 4.0)。
学習中にマスク済みコンテキストとして使われた検索パッセージの出典Sphere(CC BY-NC 4.0)は、このモデルリポジトリ自体には含まれていない。
今回の検証コード・ログは`experiments/day-057/`に置いてある。
検索ステップの「retriever」部分は、ライブのWeb検索APIを呼ぶのではなく、モデルカード自身のデモと同じ「固定文字列を返す」方式(ただし筆者が各問に対応する正しい事実パッセージを用意したもの)を使っている。
論文自体の検索インデックス(BM25 over Sphere)をフルで再現するのはそもそもスコープ外としており、QueryLMがどのようなクエリを書き、どのように文章を続けるかという定性的な観察に絞った。
