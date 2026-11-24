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

- 初回実行(セクション1〜3): CPU推論のみ。torch 2.15.0+cu132 (CPU実行)、transformers 5.24.0、Python 3.11.18。
- ローカル検証(セクション4〜5): WSL2 (Ubuntu) / Python 3.14.7 / torch 2.15.0+cu132 / transformers 5.24.0 / GPU: NVIDIA GeForce RTX 5060 Ti 16GB。README記載の手順でvenvを作り直し、モデルも取得し直した。
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
| **正解数** | | **3/8** | **2/8** | **1/8**(初出時は0/8と誤集計。1問目のJane Austenは正解) |

生成されたクエリの例(QueryLM自身が書いたもの、`querylm_query`):

- "Pride and Prejudice novel author"
- "Mongolia capital symbol gold Au"(前の問いの単語が混入している)
- "tallest mountain world answer Au symbol"(同様)

生ログは `qa_results.json` / `logs_qa_compare.txt` に全件記録。

### 分かったこと(初回実行時の考察)

> この節の1・2はローカル検証(セクション4・5)で修正された。Standardの正解数は1/8、検索ありはローカルの4条件すべてで3/8、NQ 300問では検索なしのQueryLMとStandardに差はなく、検索はプラスに働いた。

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

## 4. ローカル検証: 同じ8問をGPU/CPU・BF16/FP32で再実行

3つのスクリプトは変更せず、`run_device.py` で「モデルを載せるデバイス」と「dtype」だけを差し替えて実行した(プロンプト・greedy decoding・後処理は同一)。
ラッパーを通したCPU BF16の結果は、ラッパーなしで素のスクリプトを実行した結果と完全一致した。
採点は `grade_devices.py`(期待語が回答の1行目に含まれるか。sft-searchは1文目)で、上の表の手動採点と同じ基準。
ログと生成結果は `device_runs/<device>-<dtype>/` に置いた。

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

- **「検索させると3/8→2/8に下がった」はローカルでは再現しなかった。** 4条件すべてで(B)は3/8。差はモナリザの1問だけで、初回実行ではクエリ `Jane Austen Mona Lisa painting question` → 回答 `The Mona Lisa` だったが、ローカルの4条件はすべてクエリ `Au Mona Lisa painting artist name` → 回答 `Leonardo da Vinci`(正解)だった。FP32(CPU/GPU)でも同じ出力なので、初回実行の値はその環境でのBF16の数値差によるものと考えられる。
- 検索で崩れた2問(Pride and Prejudice→空文字列、世界最高峰→`Au`)は4条件すべてで再現した。検索で正解に変わったのはモンゴルとモナリザの2問。
- **8問のうち2問(Pride and Prejudice、金の元素記号)はfew-shot例題と同じ問題で、答えがプロンプトに書かれている。** これを除く6問では (A) 1/6(世界最高峰のみ)、(B) 2/6、(C) 0/6。
- モデルカード例(`01_reproduce_cards.py`)はCPU BF16 / CPU FP32 / GPU FP32でカード記載の出力と一致した。GPU BF16だけはStandardの回答が `Gold` ではなく `Australia` になった。
- sft-searchの幻覚のうち「ダ・ヴィンチの師がティエポロ」は4条件すべてで出た。「エベレストがインドの州にある」はBF16(CPU/GPU)でのみ出て、FP32では出なかった。
- 所要時間(8問×3条件、`02_qa_compare.py`): CPU BF16 28.6s、GPU BF16 51.2s。GPUは別プロジェクトの学習ジョブが使用率100%で使っていた最中で、速度比較にはなっていない。

## 5. ローカル検証: Natural Questions 300問に拡大

8問では1問の違いで結論が入れ替わるため、同じプロンプト・同じfew-shot・同じdecodingのまま、Natural Questionsの開発セットに広げた(`04_nq_scale.py`)。

- データ: `Tevatron/wikipedia-nq` の `nq-dev.jsonl.gz`(DPR形式。質問はNatural Questions、CC BY-SA 3.0。段落は英語Wikipedia)。ファイル先頭から、1番目のpositive passage(約100語のWikipedia段落)に正解文字列が含まれる質問を300問。
- 検索条件の `<WEB_RESPONSE>` には、モデルが書いたクエリに関係なく、その正解入りの段落を渡す(常に正しい文書が返ってくる「理想的なretriever」)。つまり(B)(D)は「良い検索結果を渡されたときに使えるか」を測っている。
- 追加条件 (D0): sft-search版で検索トークンを禁止した場合。
- 採点: SQuAD式の正規化(小文字化・句読点と冠詞の除去)後、正解文字列のいずれかが回答(ベースモデルは1行目、sft-searchは1文目)に含まれれば正解。空文字列は不正解。部分一致なので甘めの採点。
- 実行: CPU BF16(GPUは別ジョブが使用中だったためCPUで実行。8問ではCPU/GPUで結果が同じだった)、300問で3196秒。

```
$ .venv/bin/python 04_nq_scale.py 300 cpu bf16 nq_scale_results.jsonl
[04] n=300 device=cpu dtype=bf16 torch=2.15.0+cu132
[04] done in 3196s
$ python summarize_nq.py
n = 300 questions (NQ dev, DPR positive passage contains the answer)

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

A: empty answers = 11, answer is a substring of the question = 39
B: empty answers = 6, answer is a substring of the question = 67
C: empty answers = 14, answer is a substring of the question = 59
B_query: contains gold answer = 2, contains few-shot words (Jane Austen/Pride and Prejudice/Au/gold) = 235
D_query: contains gold answer = 2, contains few-shot words (Jane Austen/Pride and Prejudice/Au/gold) = 1
```

### 分かったこと

1. **検索なしでは、QueryLMとStandardに差はなかった(どちらも1/300)。** 8問での「3/8 vs 0/8(正しくは1/8)」の差は、few-shot例題と同じ2問と、世界最高峰の1問から来ていた。NQのような一般的な質問では、どちらの360Mベースモデルもほぼ答えられない。
2. **正解入りの段落を渡すと、QueryLMは1問→17問に増えた。** 検索で正解が崩れたのは1問だけ(ロンドンの水道水の水源。検索なしでは `The water in the bath is from the river Thames.`、検索ありでは質問文をそのまま返した)。8問で見えた「検索が裏目に出る」現象は存在するが、全体としては検索は明確にプラスに働いた。
3. **ベースモデルが書くクエリには、few-shot例題の単語が300件中235件で混入していた**(例: `Jane Austen last person executed ireland answer`)。それでも渡す段落が正しければ答えられる場合がある(この例の回答は `Michael Manning` で正解)。回答も `What is the chemical symbol for gold?`(43件)のように例題を復唱するものが多い。
4. **sft-search版は、段落を渡すと3/300→80/300(26.7%)まで上がった。** チャット微調整後のほうが、渡された文書を使う力ははるかに大きい。ただし8問のときの「8/8」に比べると大きく下がり、残りの約73%は段落に答えがあっても、別の内容を書き続けたり幻覚を足したりしていた。

## まとめ

- 初回の8問では「検索なしでQueryLM 3/8 > Standard 0/8」「検索させると2/8に低下」に見えたが、ローカル検証で次のように修正された: Standardは1/8(集計ミス)、検索ありは3/8(BF16の数値差。FP32・GPUを含むローカル4条件すべてで3/8)、8問中2問はfew-shot例題と同一。
- NQ 300問に広げると、検索なしではQueryLMとStandardは同じ1/300で差はなかった。360Mのベースモデル同士の閉じた知識QAでは、論文の主張する差は観察できなかった(論文の評価設定とは異なる)。
- 正解入りの段落を渡すと、QueryLMは1/300→17/300、sft-search版は3/300→80/300に上がった。検索で正解が崩れる例は300問中1問だけで、「検索が裏目に出る」は8問という小さな標本で目立っただけだった。
- ベースモデルのクエリはfew-shot例題の単語に強く引きずられる(235/300)。チャット微調整版のクエリではほぼ起きない(1/300)。
- チャット微調整版でも、段落に答えがあるのに外す問題が約73%あり、余談部分の幻覚も残る。モデルカードの「Not a product」「research artifact」という位置づけ通り、360Mクラスではまだ実用品質ではない。
- ライセンス: モデル重みはApache-2.0。sft-search版のモデルカードには、微調整データの選別にLlama 3.1 8Bを使い、Llama 3.1で生成されたSmolTalkの会話を含むため「Built with Llama」とLlama 3.1 Community Licenseの表示がある。NQの質問はCC BY-SA 3.0。事前学習テキストは英語Wikipedia(CC BY-SA 4.0)。学習中に使われた検索パッセージの出典Sphere(CC BY-NC 4.0)はこのリポジトリには含まれていない(配布物ではなく学習時のマスク済みコンテキストとして使われたのみ)。
- Routine環境・ローカル検証に関する制約: なし。Hugging Face Hubへのアクセス・モデルダウンロード・CPU推論はいずれもクラウドRoutine環境内で完結した。検索ステップの「retriever」部分のみ、ライブのWeb/Wikipedia APIを呼ばず、モデルカード自身のデモと同じ「固定文字列を返す」方式(ただし筆者が各問に対応する正しい事実パッセージを用意)を採用した。これは環境制約の回避ではなく、再現性のある比較のための意図的な設計(論文の検索インデックス自体の再現はそもそもスコープ外としていた)。
