# Day 055 検証結果: SenseNova-Loop-9B(ループ回数を1〜4回に変えて比較)

出典: https://huggingface.co/sensenova/SenseNova-Loop-9B (Apache-2.0)
量子化版: https://huggingface.co/sensenova/SenseNova-Loop-9B-AWQ (Apache-2.0、revision `8327226ffd2e33e34cb5466a0e6cccd4419bde40`)
コード: https://github.com/OpenSenseNova/SenseNova-Loop (Apache-2.0、commit `e19d54117b23e83b6719f1d17bba381b8396b3a5`)

## 0. 何を検証したか

SenseNova-Loop-9Bは、32層のデコーダのうち層4〜27(24層)を同じ重みで2回続けて実行し、1トークンあたり56回の層計算を行う「ループ型デコーダ」である(README: `Looped layer range / passes | [4, 28) / 2`)。
チェックポイントの `config.json` には `loop_settings: {start: 4, end: 28, counts: [2], eval_count: 2}` が書かれている。
同じ重みのまま、推論時のループ回数(`eval_count`)だけを1・2・3・4回に変えて、出力・perplexity・掛け算の正答率・生成速度を比べた。

注意: READMEの「Loop Scaling」節(3〜4ループで最高性能)は、`matched training and inference loops`、つまり学習時と推論時のループ回数をそろえた別モデルでの実験である。
今回は2ループで学習・公開されたチェックポイントの推論時ループ回数だけを変えており、READMEの実験とは条件が異なる。

## 1. 環境(ローカルPC, 2026-11-22)

- Windows + WSL2(Ubuntu 24.04、Linux 6.6)、AMD Ryzen 7 7700、RAM 30GB
- GPU: NVIDIA GeForce RTX 5060 Ti(16GB)、ドライバのCUDA 13.3
- Python 3.12、torch 2.11.0+cu130、transformers 5.18.0(READMEの検証済み組み合わせ)、gptqmodel 7.6.0、fla-core 0.6.0
- `causal_conv1d` は未導入(フォールバック実行の警告が出る)

```
$ git clone https://github.com/OpenSenseNova/SenseNova-Loop
$ uv venv -p 3.12 .venv
$ uv pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu130
$ uv pip install -e ./SenseNova-Loop
$ hf download sensenova/SenseNova-Loop-9B-AWQ --local-dir models/SenseNova-Loop-9B-AWQ --exclude "assets/*"
```

AWQ版のダウンロードは5.7GB。

## 2. BF16版はgated、AWQ版で進めた

```
$ curl -s https://huggingface.co/api/models/sensenova/SenseNova-Loop-9B | jq .gated
"auto"
$ curl -s https://huggingface.co/api/models/sensenova/SenseNova-Loop-9B-AWQ | jq .gated
false
$ curl -sL https://huggingface.co/sensenova/SenseNova-Loop-9B/resolve/main/config.json
Access to model sensenova/SenseNova-Loop-9B is restricted. You must have access to it and be authenticated to access it. Please log in.
```

BF16版はHugging Faceでの利用規約への同意(gated)が必要だった。
BF16の重みは9Bパラメータ×2バイトで約18GB(計算値)になり16GBのGPUには載らないため、gatedではない公式のAWQ 4bit版(READMEで「約4.9GB」)を使った。

## 3. AWQ版を公式CLIで読むと、そのままでは動かなかった

### 3-1. gptqmodelが必要(`logs/01-awq-cli-first.log`)

```
$ sensenova-loop --model-path models/SenseNova-Loop-9B-AWQ --local-files-only \
    --prompt 'What is 13 times 7? Reply with the number only.'
...
ImportError: Loading an AWQ quantized model requires gptqmodel. Please install it with `pip install gptqmodel`
```

`uv pip install gptqmodel` で依存関係ごと入れると、torch 2.15.0・transformers 5.24.0に上がり、`RuntimeError: operator torchvision::nms does not exist` で `transformers.modeling_utils` が読めなくなった。
torch 2.11.0+cu130・torchvision 0.26.0・transformers 5.18.0を制約ファイル(`constraints.txt`)で固定して入れ直すと、gptqmodel 7.6.0が入った。

### 3-2. 埋め込み層とlm_headが読み込まれず、出力が意味不明になった(`logs/02-awq-cli-gptqmodel.log`)

```
[transformers] `torch.bfloat16` is not supported for AWQ CUDA/XPU kernels yet. Casting to `torch.float16`.
SenseNovaLoopForConditionalGeneration LOAD REPORT from: models/SenseNova-Loop-9B-AWQ
lm_head.qweight                           | UNEXPECTED
lm_head.scales                            | UNEXPECTED
model.language_model.embed_tokens.qzeros  | UNEXPECTED
model.language_model.loop_gate.logits     | UNEXPECTED
lm_head.qzeros                            | UNEXPECTED
model.language_model.embed_tokens.scales  | UNEXPECTED
model.language_model.embed_tokens.qweight | UNEXPECTED
lm_head.weight                            | MISSING
model.language_model.embed_tokens.weight  | MISSING
...
转型发展 aneh … Mittag fem转型发展超高的3 creden теряет بعضهم应邀ComputedStyle electrode应邀 ...
```

`13 times 7` への答えが、多言語の無意味なトークン列になった。
AWQ版の `config.json` は `quantization_config.lm_head: true` と `embedding: {bits: 4, group_size: 128, layout: "row_major"}` を持ち、埋め込み層とlm_headも4bitで保存されている。
Transformers + gptqmodelはこの2つを量子化済みとして扱わず、`weight` が無いため乱数で初期化したまま推論していた。
AWQ版のREADMEは、AWQの配信方法としてLightLLMの `main` ブランチを案内している(Transformersでの読み込み手順はBF16版向けの記述のみ)。

### 3-3. 埋め込み層とlm_headを自分で逆量子化した(`awq_fix.py`、`logs/03-order-search-loop2.log`)

テンソルの形:

```
model.language_model.embed_tokens.qweight [248320, 512] I32
model.language_model.embed_tokens.qzeros  [248320, 4]   I32
model.language_model.embed_tokens.scales  [248320, 32]  F16
lm_head.qweight [4096, 31040] I32
lm_head.qzeros  [32, 31040]   I32
lm_head.scales  [32, 248320]  F16
```

`w = (q - zero) * scale`(group_size 128)で戻し、4bit値の並び順(AWQ gemm形式の `[0,2,4,6,1,3,5,7]` か、素直な順か)を埋め込み・lm_headそれぞれで試した。
英語の参照文(71トークン)の平均NLLで判定した(ループ2回)。

| 埋め込みの並び | lm_headの並び | 英語NLL |
|---|---|---|
| AWQ | AWQ | 20.2624 |
| AWQ | 素直 | 24.6403 |
| **素直** | **AWQ** | **1.0140** |
| 素直 | 素直 | 17.5582 |

埋め込み=素直な順、lm_head=AWQ順でNLLが1.01まで下がり、`13 times 7` に `91` と答えるようになった。
以降はこの組み合わせを使う。
この逆量子化は筆者の実装であり、公式の推論経路(LightLLM等)と完全に同じ数値になる保証はない。

(初回の実行は、モデルがfloat16にキャストされているのに逆量子化した重みをbfloat16で入れたため `RuntimeError: expected mat1 and mat2 to have the same dtype` で止まった。筆者のスクリプトの誤りで、既存重みのdtypeに合わせて解消した。)

## 4. ループ回数を1〜4回に変えた比較(`run_loops.py`、`logs/04-loops-1to4.log`、`out_loops.json`)

一度読み込んだモデルの実行計画だけを、リポジトリの `execution_plan()` で作り直して切り替えた(重みは同じ)。
`flash-linear-attention`(fla-core 0.6.0)を入れて実行した。
生成はgreedy、thinking無効、最大200トークン(掛け算は16トークン)。

### 4-1. 数値のまとめ

| ループ回数 | 層の実行回数/トークン | 英語perplexity | 日本語perplexity | 掛け算20問の正解 | 生成速度 |
|---|---|---|---|---|---|
| 1 | 32 | 4.959 | 38.449 | 1/20 | 2.69 tok/s |
| **2(既定)** | **56** | **2.754** | **10.120** | **19/20** | **1.40 tok/s** |
| 3 | 80 | 3.285 | 15.038 | 18/20 | 0.94 tok/s |
| 4 | 104 | 5.245 | 28.666 | 11/20 | 0.81 tok/s |

- perplexityは、英語71トークン・日本語67トークンの参照文(`run_loops.py` 内 `REFERENCE_TEXTS`)に対する値。
- 掛け算は3桁×2桁を20問(`random.Random(0)` で生成)、`Reply with the number only.` で答えさせ、回答の最後の数値で採点した(`regrade.py`、`logs/05-regrade.log`)。
  数字を全部つなげて採点した初回の集計では、ループ3回が17/20、ループ4回が10/20だった(「438 × 70 = 30,660」のように式ごと答えた回答を誤って不正解にしていた)。
- 生成速度は、6つのプロンプトのうち最初の1つ(ウォームアップを含む)を除いた5つの合計出力トークン数÷合計時間。
- 最大GPUメモリ確保量は8.28GiB(`torch.cuda.max_memory_allocated`)。自分で逆量子化したfloat16の埋め込み層とlm_head(各248320×4096)を含む。

### 4-2. 掛け算の誤答の例

| ループ | 問題 | 正解 | 出力 |
|---|---|---|---|
| 1 | 964×59 | 56876 | 55876 |
| 1 | 588×55 | 32340 | 23940 |
| 2 | 733×42 | 30786 | 30796(2ループ唯一の誤答) |
| 3 | 623×72 | 44856 | 4486 |
| 4 | 964×59 | 56876 | 5684 |
| 4 | 876×63 | 55188 | 57,108 |

### 4-3. 文章題・コードの出力

**バットとボール**(正解: 5セント)

- ループ1: `The ball costs $0.15. If the ball is $x, the bat is $x + 1.00, and together they total $1.10, so 2x + 1.00 = 1.10 → x = 0.15.`(式は正しいが計算を誤った)
- ループ2: `... 2x + 1.00 = 1.10 \implies 2x = 0.10 \implies x = 0.05 ... **The ball costs 5 cents.**`
- ループ3: `The ball costs **$0.05**.`
- ループ4: `**The ball costs 5 cents.**`

**5台の機械で5分に5個**(正解: 5分)

- ループ1: 手順を書き始めたあと `100 machines working simultaneously can produce 100 individual individual individual ...` と同じ単語を200トークンの上限まで繰り返した。
- ループ2〜4: `It would take **5 minutes**.`

**Sallyの姉妹**(正解: 1人)

- ループ1: `Since Sally is one of those 2 sisters, she has 1 sister.` と正しい推論を書いたが、`Wait, let me reconsider.` と同じ推論を繰り返し、200トークンで打ち切られた。
- ループ2: `Sally has **2** sisters.`(誤り)
- ループ3: `Sally has **2** sisters.`(誤り)
- ループ4: `Sally has **2** sisters. ... meaning there are 3 girls in total.`(誤り)

**日本の首都**: ループ1〜4すべて `日本の首都は東京です。`

**fib(n)のコード**

- ループ1: `a = b` → `b = a + b` と2行に分けて代入しており、`b` が常に `2*b` になる誤ったコード。
- ループ2・3: `a, b = b, a + b` の正しいコード(`for _ in range(n - 1)` で `return b`)。
- ループ4: `n < 0` で `ValueError` を投げる、正しいコード。

## 5. まとめ

- 公開チェックポイントは2ループ前提で、推論時のループ回数を1回に減らすと、perplexity(英語2.75→4.96、日本語10.1→38.4)・掛け算(19/20→1/20)・文章題・コードのすべてで明確に悪化した。
- 3回・4回に増やしても改善はせず、perplexityと掛け算の正答率は下がった(4ループで11/20)。速度はループ回数にほぼ比例して落ちた(2.69→1.40→0.94→0.81 tok/s)。
- 「同じ重みを2回通すこと」が性能に効いていることは1ループとの比較で確認できたが、それは学習時のループ回数に合わせた場合であり、推論時に回数だけ増やしても性能は上がらなかった。
- Sallyの問題は2〜4ループがすべて誤り(2人)で、ループ1だけが途中で「1人」と正しく推論した(ただし繰り返しで打ち切られた)。
- 公式AWQ版はTransformers + gptqmodelでは埋め込み層とlm_headが読まれず、そのままでは意味のない出力になった。今回の数値は、筆者が逆量子化した重みを差し込んだ状態でのもの。

## 6. 未検証

- BF16版(gated、計算上約18GB)での同じ比較。
- 公式に案内されているLightLLM / vLLM / SGLangでの推論。
- READMEのベンチマーク(GAIA・BIRD・Terminal-Bench 2.1等)の再現。
- 画像入力。
