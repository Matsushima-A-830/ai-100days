# Day 057 検証結果: QueryLM (search-native pretraining) vs Standard baseline — 360M

出典: 論文 [Search From the Start: Search-Native Pretraining for Language Models](https://arxiv.org/abs/2611.26809)
(Ponkshe, Je, Taga, Raffel, Jaggi。EPFL/University of Toronto)。
モデル群: https://huggingface.co/collections/Kausp11/search-native-pretraining (Apache-2.0)。
使用した3モデル:

- `Kausp11/querylm-wiki-360m`(search-native事前学習、ベースモデル)
- `Kausp11/standard-wiki-360m`(同architecture・同compute、検索ブロックなしのプレーンテキストのみで事前学習したベースライン)
- `Kausp11/querylm-wiki-360m-sft-search`(QueryLMをチャット形式で1エポック微調整した版)

いずれも361.8Mパラメータ(BF16)、SmolLM2-360M構成(32層、width 960、15 heads)、transformersでロード可能(カスタムコード不要)。

## 環境

- CPU推論のみ(GPU不要)。torch 2.15.0+cu132 (CPU実行)、transformers 5.24.0、Python 3.11.18。
- モデル重みはHugging Face Hubから直接ダウンロード(認証不要、合計約2.1GB)。

## 1. モデルカードの使用例をそのまま再現

`01_reproduce_cards.py` でQueryLM / Standardそれぞれのモデルカード記載のPythonコードを一字一句そのまま実行した。

```
=== QueryLM (search-native) ===
WEB_QUERY ids: 49152 49153
query : Jane Austen Pride and Prejudice capital Australia answer
answer: The capital of Australia

=== Standard (no-search baseline) ===
answer: Gold
```

いずれもモデルカードに記載された出力(`query : Jane Austen Pride and Prejudice capital Australia answer` / `answer: The capital of Australia` / standard版 `answer: Gold`)と完全に一致した。モデルカードの記述は誇張ではなく、公開された重みで素直に再現できた。

## 2. 8問の知識QAで3条件を比較

`02_qa_compare.py`。全て greedy decoding(`do_sample=False`)。3条件:

- **(A) querylm_no_search**: QueryLMで`<WEB_QUERY>`トークンを`bad_words_ids`で禁止し、検索を使わせない(Standardと同じ情報量での比較)。
- **(B) querylm_with_search**: QueryLM自身に検索クエリを書かせ、各問に対して筆者が事前に用意した正しい参考パッセージ(Wikipedia由来の事実、モデルカードの固定文字列デモと同じ方式)を`<WEB_RESPONSE>`として渡して続きを生成させる。
- **(C) standard**: Standardベースラインで検索なし(そもそも検索トークンを学習時に見ていない)。

| 質問 | 正解 | (A) QueryLM 検索なし | (B) QueryLM 検索あり | (C) Standard |
|---|---|---|---|---|
| Pride and Prejudiceの作者は? | Jane Austen | Jane Austen ✅ | (空文字列) ❌ | Jane Austen ✅ |
| 金の元素記号は? | Au | Au ✅ | Au ✅ | Gold? ❌ |
| オーストラリアの首都は? | Canberra | The capital of Australia ❌(非回答) | The capital of Australia ❌(非回答) | Gold ❌ |
| モンゴルの首都は? | Ulaanbaatar | The capital of Mongolia? ❌(非回答) | Ulaanbaatar ✅ | Gold ❌ |
| モナリザを描いたのは? | Leonardo da Vinci | Jane Austen ❌ | The Mona Lisa ❌(非回答) | The Mona Lisa? ❌(非回答) |
| ベルリンの壁崩壊は何年? | 1989 | 1949 ❌ | The Berlin Wall fell? ❌(非回答) | 1961 ❌ |
| 世界最高峰は? | Mount Everest | Mount Everest ✅ | Au ❌(検索で悪化) | The highest mountain in the world? ❌(非回答) |
| 月に最初に降りたのは誰? | Neil Armstrong | John Lennon ❌ | (空文字列) ❌ | The first person to walk on the Moon? ❌(非回答) |
| **正解数** | | **3/8** | **2/8** | **0/8** |

生成されたクエリの例(QueryLM自身が書いたもの、`querylm_query`):

- "Pride and Prejudice novel author"
- "Mongolia capital symbol gold Au"(前の問いの単語が混入している)
- "tallest mountain world answer Au symbol"(同様)

生ログは `qa_results.json` / `logs_qa_compare.txt` に全件記録。

### 分かったこと

1. **検索を使わない状態でも、QueryLMはStandardより知識QAに強い**(3/8 vs 0/8)。同じアーキテクチャ・同じcompute予算で、学習テキストに検索ブロックを混ぜて事前学習しただけで、素の知識定着量に差が出ている。これは論文の主張(同FLOPsでQueryLMがstandardベースラインに勝つ)の方向性と一致する、360Mという最小サイズでの定性的な観察。
2. **ただし、ベースモデルに実際に検索を使わせても、正解に書き換わらないことが多い**。モンゴルの首都では検索が有効に働いた(❌→✅)が、Pride and Prejudiceと世界最高峰では、検索前は正解していたのに検索を使わせた途端に空文字列や無関係な単語("Au")に変わってしまった。ベースモデル(チャット微調整なし)は「検索結果を使って答えを言い直す」という形式自体が不安定で、たまたま上手くいく場合と裏目に出る場合が混在している。
3. **クエリの質自体も怪しい**。QueryLMが書くクエリには、直前の例題やその前の質問の単語が紛れ込むことがある("tallest mountain world answer **Au symbol**" — 直前の金の問題の単語が残っている)。360Mという極小サイズでは、少数の例を見ただけで文脈の切り替えがうまくいかないことがある。
4. **StandardはQ&A形式そのものの維持が苦手**("Gold?"、"The Mona Lisa?"のように、質問文をそのまま繰り返す/疑問形で返すパターンが多い)。これは「検索ブロックを学習していない」こと自体の影響というより、360Mという極小モデル・Wikipediaのみの学習データという条件下での few-shot 形式維持の弱さの可能性がある。

## 3. チャット微調整版(sft-search)での比較

`03_sft_variant.py`。同じ8問・同じ参考パッセージで `querylm-wiki-360m-sft-search`(QueryLMをチャット形式・検索込みの対話データで1エポック微調整した版)を試した。

| 質問 | クエリ | 回答(冒頭) |
|---|---|---|
| Pride and Prejudiceの作者は? | Pride and Prejudice novel author | "Jane Austen, author of Pride and Prejudice, was a British writer..." ✅ |
| 金の元素記号は? | gold chemical symbol gold | "Gold is a chemical element with the symbol Au and atomic number 79..." ✅ |
| オーストラリアの首都は? | Australia capital city name | "Canberra is the capital city of Australia..." ✅ |
| モンゴルの首都は? | Mongolia capital city name | "Ulaanbaatar is the capital and largest city of Mongolia..." ✅ |
| モナリザを描いたのは? | Mona Lisa painting artist name | "Leonardo da Vinci was a painter of the Renaissance period... **He was a pupil of the painter and architect, Giovanni Battista Tiepolo**" ✅(本題)/ ❌(余談部分が誤り) |
| ベルリンの壁崩壊は何年? | Berlin Wall fall date year | "9 November 1989\n\nThe Berlin Wall fell on 9 November 1989..." ✅ |
| 世界最高峰は? | tallest mountain world tallest mountain name | "The tallest mountain in the world is Mount Everest... **located in the Indian state of Himachal Pradesh**" ✅(本題)/ ❌(位置の余談が誤り。実際はネパールと中国の境) |
| 月に最初に降りたのは誰? | first person walk on the Moon name | "Neil Armstrong was an American astronaut who became the first person to walk on the Moon, on July 20, 1969..." ✅ |

**8問すべてで本題の答えが正しく、渡したパッセージの事実を正確に取り込めている。** ベースモデルで見られた「検索したのに空文字列/無関係な単語になる」という不安定さは、チャット微調整後は見られなかった。ただし2問(モナリザ、エベレスト)では、本題は正しいまま、文章を続けるうちに余談部分で事実と異なる内容(ダ・ヴィンチの師匠としてティエポロを挙げる、エベレストをインドの州にあると書く)を生成しており、小型モデルらしい幻覚は残っている。また同じ語句の繰り返し("the capital of the Australian Capital Territory"を連呼する等)も目立つ。

生ログは `sft_results.json` / `logs_sft_variant.txt` に全件記録。

## まとめ

- 検索ネイティブな事前学習(QueryLM)は、検索を使わなくても同条件のStandardベースラインより知識QAが強い、という方向性は360Mの小型モデルでも定性的に確認できた。
- しかしベースモデルのまま検索を使わせても、安定して賢くなるわけではなく、むしろ既知の正解を崩すケースもあった。「検索機能を安定して使いこなす」にはチャット微調整(sft-search)が重要に見える。
- チャット微調整版は渡された事実の中核部分を正確に使えるが、それでも余談部分では幻覚が残る。モデルカードの「Not a product」「research artifact」という位置づけ通り、360Mクラスではまだ実用品質ではない。
- ライセンス: モデル重みはApache-2.0。事前学習テキストは英語Wikipedia(CC BY-SA 4.0)。学習中に使われた検索パッセージの出典Sphere(CC BY-NC 4.0)はこのリポジトリには含まれていない(配布物ではなく学習時のマスク済みコンテキストとして使われたのみ)。
- Routine環境・ローカル検証に関する制約: なし。Hugging Face Hubへのアクセス・モデルダウンロード・CPU推論はいずれもクラウドRoutine環境内で完結した。検索ステップの「retriever」部分のみ、ライブのWeb/Wikipedia APIを呼ばず、モデルカード自身のデモと同じ「固定文字列を返す」方式(ただし筆者が各問に対応する正しい事実パッセージを用意)を採用した。これは環境制約の回避ではなく、再現性のある比較のための意図的な設計(論文の検索インデックス自体の再現はそもそもスコープ外としていた)。
