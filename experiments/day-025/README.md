# Day 025: AKV (Cache Engineering for Agents) — drop/reposの縮小版概念実証

- 出典(論文): https://huggingface.co/papers/2610.28577
- 出典(公式コード): https://github.com/thu-nics/AKV (Apache-2.0, 清華大学・香港中文大学)
- 検証に使ったモデル: https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct (Apache-2.0)

## やったこと

論文のサービング実験(A800 80GB×8枚・GPT-OSS-120B等)はこのRoutineのCPU実行環境では
再現不可能なため、論文の核である2つの操作、

- **drop**: 不要になったKVキャッシュのエントリをテキストを書き換えずに直接削除する
- **repos**: 削除によってずれた残存キーのRoPE位置エンコーディング(回転角)を付け替える

を、公式コードを使わずに自分で実装し、CPU上で動くRoPEベースの小型モデル
(`HuggingFaceTB/SmolLM2-135M-Instruct`, 135M)に対して実際に動かして確認した。

1. `akv_poc.py` — 架空の在庫棚卸しエージェントの会話(system + ユーザー依頼 + tool応答4回
   + 最終質問)を作り、`full`(無管理)/`summarize`(既存のcontext engineering)/
   `drop`(位置補正なしの素朴な削除)/`drop+repos`(削除+RoPE回転の付け替え)の4方式を
   実装・実行し、最終キャッシュ長・management操作の時間・最終応答に対するloss(perplexity)
   を比較した。
2. `akv_generate_check.py` — 同じ4方式のキャッシュに対して実際に自由生成(greedy)させ、
   出てきたテキストをそのまま記録した(モデルが小さすぎて算術自体は正解できなかったが、
   cacheを操作しても出力が自然文として崩壊しないかの定性確認として使った)。
3. 結果は `results.md` に正直に記録した(自由生成がどの方式でも不正解だった事実も含む)。

## 実装のポイント: reposはどう実装したか

RoPEは2次元回転の合成則 `R(a)R(b) = R(a+b)` が成り立つ。つまり、位置pで既に回転済みの
キャッシュ済みキーに、追加のデルタ回転`R(delta)`をそのまま乗せれば、逆回転して
作り直さずに「位置p+delta相当のキー」に変換できる。これを`rotate_keys_by_delta()`で
実装し、モデル自身の`model.model.rotary_emb`モジュール(Llama系アーキテクチャが
標準で持つRoPE計算モジュール)を使ってcos/sinを計算することで、モデルの実装と
完全に同じ回転を再現している(theta計算を独自実装していない)。

## ディレクトリ

- `akv_poc.py` — 4方式の比較実験本体
- `akv_generate_check.py` — 自由生成での補助確認
- `results_raw.json` — `akv_poc.py`の生の実行結果(JSON)
- `results.md` — 実測結果・実行ログ・正直な限界の記録
- `requirements.txt` — 検証に使ったPythonパッケージ

## 再現手順

```bash
# Python 3.11、torch/transformersをインストール(CPUのみで動く。GPU不要)
python3 -m pip install torch transformers

# 比較実験本体(4方式×5回、結果はJSONで標準出力+results_raw.jsonに保存)
python3 experiments/day-025/akv_poc.py

# 自由生成での補助確認(akv_poc.pyと同じディレクトリで実行する必要あり)
cd experiments/day-025 && python3 akv_generate_check.py
```

初回実行時は `HuggingFaceTB/SmolLM2-135M-Instruct` の重み(数百MB)をHugging Face Hubから
ダウンロードする。APIキー・トークンは不要(パブリックモデル)。
