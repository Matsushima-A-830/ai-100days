# Day 025 検証結果: AKV (Cache Engineering for Agents) — drop/reposの縮小版概念実証

検証日: 2026-10-23
検証対象: https://huggingface.co/papers/2610.28577 (コード: https://github.com/thu-nics/AKV 、清華大学・香港中文大学、2026-10-21投稿、HF Daily Papers 2026-10-22時点4位・109 upvote)

## 0. 検証のスコープ(正直な前提)

論文本体のサービング実験はA800 80GB×8枚・GPT-OSS-120B等の大規模モデル前提で、このRoutineの
CPU実行環境ではフル再現は不可能。そのため、論文のベンチマーク数値(3モデル×4ベンチマークの
平均スコア+1.7pt・コスト-27.7%など)を再現する試みは最初から行っていない。

代わりに、論文の核となる2つの操作のアイデア、

- **drop**: 不要になったKVキャッシュのエントリを、履歴テキストを書き換えずに直接削除する
- **repos**: 削除によってずれた残存キーのRoPE位置エンコーディング(回転角)を付け替える

が、実際にモデルの中で機能するかどうかを、CPU上で動く小型のRoPEベースモデル
(`HuggingFaceTB/SmolLM2-135M-Instruct`, 135Mパラメータ, Llama系アーキテクチャ,
`rope_theta=100000`)に対して自分で実装し、実測した。コードは `akv_poc.py`。

評価タスクは論文のベンチマークではなく、自分で作った架空の在庫棚卸しエージェントの
会話(system + ユーザー依頼 + 4回のtool呼び出し応答 + 最終質問)。4回のtool応答のうち
最初の2つ(shelf A1, A2)が「古くなった履歴」の役割を果たす。

## 1. 比較した4方式

| 方式 | 何をするか |
|---|---|
| `full` | 履歴を一切圧縮しない(ベースライン) |
| `summarize` | 既存のcontext engineering。古い2つのtool応答をテキストで要約し、system+要約+残り2ブロックをゼロから再prefillする |
| `drop` | 古い2つのtool応答に対応するKVキャッシュのエントリを直接削除する(**位置の補正はしない**, naive drop) |
| `drop+repos` | `drop`に加え、削除によって配列上の位置がずれた残存ブロック(tool応答3,4)のキーに、RoPEの追加回転(delta = -削除トークン数)を適用して位置エンコーディングを付け替える |

RoPEは2次元回転の合成則 `R(a)R(b) = R(a+b)` が成り立つため、キャッシュ済みのキーに
追加のデルタ回転をそのまま乗せるだけで「位置p+delta相当のキー」に変換できる。
これは逆回転して作り直す必要がない、まさに論文が言う「履歴を書き換えずにアクティブな
KVキャッシュを直接操作する」という発想そのものであり、`rotate_keys_by_delta()`として
実装した(モデル自身の`model.model.rotary_emb`モジュールを使い、theta計算を独自実装せず
モデルと完全に同じ回転を再現している)。

## 2. 実測結果(5回実行の平均、`results_raw.json`に生データ)

| 方式 | 最終キャッシュ長(トークン) | 最終応答のloss | perplexity | management操作の時間 | prefillの時間 |
|---|---|---|---|---|---|
| full | 423 | 0.8047 | 2.236 | 0.00 ms | 472.2 ms |
| summarize | 257 (-39.2%) | 1.0251 | 2.787 | 180.86 ms | 0.0 ms(再prefillに統合) |
| drop | 223 (-47.3%) | **1.4868** | 4.423 | 1.49 ms | 457.0 ms |
| drop+repos | 223 (-47.3%) | **0.8386** | 2.313 | 6.13 ms | 467.3 ms |

(「最終応答のloss」は、system+残りの履歴+最終質問を条件として、正解テキスト
「The final total count of working thermal printers is 14.」に対するcross entropy損失。
5回とも完全に同じ値になった = モデルはeval modeで決定的に動作しており、再現性は確認済み)

(「management操作の時間」は、`summarize`では要約テキスト込みの全体再prefillにかかった
時間そのもの、`drop`/`drop+repos`ではキャッシュのスライス(+回転)操作だけにかかった
時間を、その前後のprefillと分離して計測したもの)

### 読み取れること

1. **キャッシュサイズ**: `drop`/`drop+repos`は`summarize`よりキャッシュが小さい(223 vs 257トークン)。
   要約文を追加で生成・保持する必要がないため。
2. **品質(loss)**: `drop`(位置補正なし)は`full`より大幅に悪化(0.805→1.487、perplexityは約2倍)。
   `drop+repos`はほぼ`full`と同水準まで回復する(0.805→0.839)。つまり
   **「履歴を直接削るだけ」では位置エンコーディングの不整合で品質が落ちるが、
   RoPE回転の付け替え(repos)でその劣化がほぼ解消される**ことが、この縮小実験でも確認できた。
3. **コスト**: `drop+repos`のmanagement操作自体は6.13msで、`summarize`の全体再prefill(180.86ms)の
   約1/30。`drop`単体はさらに軽い(1.49ms、回転計算が無い分)。削除対象が増えるほど
   `summarize`の再prefillコストは線形に増えるが、`drop`/`repos`のコストは削除対象の
   トークン数にほぼ依存せず、スライスと回転行列の掛け算だけで済む。

これは論文が主張する「要約はキャッシュを無効化し再prefillのコストを招く」
「drop/reposは履歴を書き換えずに直接操作できる」という2つの主張を、
135Mパラメータという小さなスケールながら、実際に数値で確認できた結果だと言える。

## 3. 自由生成での確認(`akv_generate_check.py`)、そして率直な限界

上記のlossは「正解テキストが与えられた場合の尤度」を見ているだけなので、実際に
モデルに自由生成(greedy)させて最終応答がどうなるかも確認した。結果は以下の通り
(すべて実際にモデルが生成したテキストそのまま、改変なし)。

```
=== full ===
"calling tool: scan_shelf(shelf='B3')"

=== drop (naive, no repos) ===
'Based on all shelves scanned so far, what is the final total count of working thermal printers.'

=== drop+repos ===
'Based on the total count of working thermal printers scanned so far, the final total count is 20.'

=== summarize ===
'Shelf B1: 4 + 2 = 6\nShelf B2: 6 + 5'
```

**正直に書くと、どの方式でも135Mモデルは「14」という正解には到達しなかった。**
`full`はさらに別のshelfをスキャンしようとして質問に答えず、`drop`は質問文を
オウム返しするだけで数値を出さず、`drop+repos`は数値(20、不正解)を出したが
計算は誤っている。`summarize`は足し算を途中からやり直そうとしている。

これは135Mという非常に小さいモデルが、4つのツール応答にまたがる数値を正確に
足し合わせる、という複数ステップの算術推論タスク自体の能力的な限界であり、
**cache方式の違いによる結果ではない**(`full`ですら正解していない)。したがって、
この自由生成の結果は「どの方式が優れているか」を測る根拠には使わず、上記2節の
強制尤度(loss/perplexity)を主指標として採用した。自由生成の結果はあくまで
「cache操作をしてもモデルの出力が意味のある自然文として崩壊しない(特に
`drop+repos`は文法的に一貫した文を生成できている)」という補助的な定性確認として
記録する。

## 4. 実行ログ

```
$ python3 experiments/day-025/akv_poc.py
(省略: 重みダウンロードの進捗バー、distutils-precedenceの無害な警告)
[
  {
    "policy": "full",
    "final_cache_len": 423,
    "prefill_seconds": 0.4721776026000043,
    "management_seconds": 0.0,
    "answer_seconds": 0.07232684119999248,
    "answer_loss": 0.8046714067459106,
    ...
  },
  {
    "policy": "summarize",
    "final_cache_len": 257,
    "prefill_seconds": 0.0,
    "management_seconds": 0.1808566902000166,
    "answer_seconds": 0.06551806859999942,
    "answer_loss": 1.0250537395477295,
    ...
  },
  {
    "policy": "drop",
    "cache_len_before_drop": 423,
    "dropped_tokens": 200,
    "final_cache_len": 223,
    "prefill_seconds": 0.45696398020002105,
    "management_seconds": 0.0014907943999787677,
    "answer_seconds": 0.06705729980003525,
    "answer_loss": 1.4868128299713135,
    ...
  },
  {
    "policy": "drop+repos",
    "cache_len_before_drop": 423,
    "dropped_tokens": 200,
    "final_cache_len": 223,
    "prefill_seconds": 0.4672683887999938,
    "management_seconds": 0.0061286439999776125,
    "answer_seconds": 0.06502765559998806,
    "answer_loss": 0.8386205434799194,
    ...
  }
]
```

実行環境: Python 3.11.17, torch 2.14.1+cu130, transformers 5.20.2, CPU実行(4コア)、
`HuggingFaceTB/SmolLM2-135M-Instruct`。全4方式×5回の実行で `time python3 akv_poc.py` の
`real`時間は13.3〜13.7秒程度(モデルロードを含む)。生データは `results_raw.json` 参照。

## 5. ライセンス・出典

- 論文: https://huggingface.co/papers/2610.28577 (清華大学・香港中文大学)
- 公式コード: https://github.com/thu-nics/AKV (Apache-2.0。このRoutineでは公式コードを
  一切使わず、論文の`drop`/`repos`というアイデアだけを読み取って自分で再実装したため、
  転載や依存の問題はない)
- 検証に使ったモデル: https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct
  (Apache 2.0, HuggingFaceTB/Hugging Face)
- 追加の有料APIキーは不要。GPU不要(CPU実行)。
