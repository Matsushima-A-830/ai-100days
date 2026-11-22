---
title: "同じ重みを2回通すSenseNova-Loop-9B、ループを1回にすると掛け算の正解が20問中19問から1問に落ちた"
emoji: "🔁"
type: "tech"
topics: ["ai", "llm", "transformers", "quantization", "python"]
published: false
---

## これは何を試した記事か

SenseTimeが公開した[SenseNova-Loop-9B](https://huggingface.co/sensenova/SenseNova-Loop-9B)(Apache-2.0)を手元のGPUで動かし、「同じ重みを何回通すか」を変えて出力を比べた記事である。
このモデルは32層のデコーダのうち、層4〜27の24層を同じ重みのまま2回続けて実行する。
保存している層は32層分だけだが、1トークンあたりの層計算は56回になり、READMEでは「約14.6B相当の推論計算」と説明されている。

チェックポイントの設定ファイルには、このループ回数が `eval_count: 2` として書かれている。
そこで、読み込んだ重みはそのままに、推論時のループ回数だけを1・2・3・4回に切り替えて、何が変わるかを確かめた。

- 出典: https://huggingface.co/sensenova/SenseNova-Loop-9B (Apache-2.0、2026-11-17公開)
- AWQ版: https://huggingface.co/sensenova/SenseNova-Loop-9B-AWQ (Apache-2.0)
- コード: https://github.com/OpenSenseNova/SenseNova-Loop (Apache-2.0、検証コミット `e19d541`)

## 環境

| 項目 | 内容 |
|---|---|
| GPU | NVIDIA GeForce RTX 5060 Ti(16GB) |
| CPU / RAM | AMD Ryzen 7 7700 / 30GB |
| OS | Windows + WSL2(Ubuntu 24.04) |
| Python / torch / transformers | 3.12 / 2.11.0+cu130 / 5.18.0 |
| 量子化ライブラリ | gptqmodel 7.6.0 |

## BF16版はgatedなので、公式AWQ版を使った

BF16版のリポジトリは、Hugging Faceで利用規約に同意しないとダウンロードできない(gated)設定になっていた。

```bash
$ curl -sL https://huggingface.co/sensenova/SenseNova-Loop-9B/resolve/main/config.json
Access to model sensenova/SenseNova-Loop-9B is restricted. You must have access to it and be authenticated to access it. Please log in.
```

BF16の重みは9Bパラメータ×2バイトで約18GBになり、16GBのGPUには載らない。
公式が同時に出しているAWQ 4bit版はgatedではなく、READMEでは重みが約4.9GBとされているので、こちらを使った。

```bash
$ git clone https://github.com/OpenSenseNova/SenseNova-Loop
$ uv venv -p 3.12 .venv
$ uv pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu130
$ uv pip install -e ./SenseNova-Loop
$ hf download sensenova/SenseNova-Loop-9B-AWQ --local-dir models/SenseNova-Loop-9B-AWQ --exclude "assets/*"
```

## AWQ版は、公式CLIでそのまま読むと意味のない出力になった

リポジトリ同梱のCLIでAWQ版を読むと、まず `gptqmodel` が必要だと言われた。

```bash
$ sensenova-loop --model-path models/SenseNova-Loop-9B-AWQ --local-files-only \
    --prompt 'What is 13 times 7? Reply with the number only.'
...
ImportError: Loading an AWQ quantized model requires gptqmodel. Please install it with `pip install gptqmodel`
```

`gptqmodel` を依存関係ごと入れると、torchが2.15.0、transformersが5.24.0に上がり、`RuntimeError: operator torchvision::nms does not exist` でtransformers自体が読めなくなった。
torch・torchvision・transformersを制約ファイルで固定して入れ直すと、gptqmodel 7.6.0が入り、推論まで進んだ。
ところが、出てきた答えは次のとおりだった。

```
[transformers] `torch.bfloat16` is not supported for AWQ CUDA/XPU kernels yet. Casting to `torch.float16`.
SenseNovaLoopForConditionalGeneration LOAD REPORT from: models/SenseNova-Loop-9B-AWQ
lm_head.qweight                           | UNEXPECTED
model.language_model.embed_tokens.qweight | UNEXPECTED
...
lm_head.weight                            | MISSING
model.language_model.embed_tokens.weight  | MISSING
...
转型发展 aneh … Mittag fem转型发展超高的3 creden теряет بعضهم应邀ComputedStyle electrode应邀 ...
```

AWQ版の設定には `quantization_config.lm_head: true` と `embedding: {bits: 4, layout: "row_major"}` があり、埋め込み層と出力層(lm_head)まで4bitで保存されている。
Transformers + gptqmodelはこの2つを量子化済みの層として読まず、`weight` が無いとして乱数で初期化したまま推論していた。
AWQ版のREADMEがAWQの配信先として案内しているのはLightLLMで、Transformersでの読み込み手順はBF16版向けの記述しかない。

## 埋め込み層とlm_headを自分で戻した

量子化された値は `(4bit値 - ゼロ点) × スケール` で元に戻せる。
分からなかったのは、32bit整数1個に詰められた8個の4bit値の並び順だった。
AWQの行列積用の並び(`[0,2,4,6,1,3,5,7]`)と素直な並びの両方を、埋め込み層とlm_headそれぞれで試し、英語の参照文(71トークン)に対する平均損失(NLL)で比べた。

| 埋め込みの並び | lm_headの並び | 英語NLL |
|---|---|---|
| AWQ | AWQ | 20.2624 |
| AWQ | 素直 | 24.6403 |
| 素直 | AWQ | 1.0140 |
| 素直 | 素直 | 17.5582 |

埋め込みを素直な並び、lm_headをAWQの並びにしたときだけ損失が1.01まで下がり、`13 times 7` に `91` と答えた。
以降の数値は、この組み合わせで逆量子化した重みを差し込んだ状態のものである。
公式の推論経路と完全に同じ数値になる保証はない。

## ループ回数を1〜4回に切り替える

ループの実行順は、リポジトリの `execution_plan()` が設定から作っている。
一度読み込んだモデルに対して、設定の `eval_count` を書き換えた実行計画を作り直すだけで、重みを読み直さずにループ回数を変えられた。

```python
def set_loops(model, count):
    text = model.model.language_model
    raw = model.config.to_dict()
    raw["loop_settings"] = dict(raw["loop_settings"], counts=[count], eval_count=count)
    plan = execution_plan(raw)
    text._loop_plan = plan
    text._loop_cache_config = copy.deepcopy(text.config)
    text._loop_cache_config.num_hidden_layers = len(plan)
    text._loop_cache_config.layer_types = [text.config.layer_types[i] for i in plan]
    return len(plan)
```

各ループ回数で、次の3種類を測った。
生成はすべてgreedy、thinkingは無効にした。

- 英語(71トークン)と日本語(67トークン)の参照文に対するperplexity
- 3桁×2桁の掛け算20問(`Reply with the number only.`、回答の最後の数値で採点)
- 文章題3問・日本語の質問・Pythonコードの生成(最大200トークン)

## 結果: 2回がいちばん良く、1回は大きく崩れた

```
===== loops=1 (decoder layer executions per token: 32) =====
[nll en] loss=1.6011 ppl=4.959
[nll ja] loss=3.6493 ppl=38.449
[mul] 1/20 correct
===== loops=2 (decoder layer executions per token: 56) =====
[nll en] loss=1.0129 ppl=2.754
[nll ja] loss=2.3145 ppl=10.12
[mul] 19/20 correct
```

| ループ回数 | 層の実行回数 | 英語perplexity | 日本語perplexity | 掛け算 | 生成速度 |
|---|---|---|---|---|---|
| 1 | 32 | 4.959 | 38.449 | 1/20 | 2.69 tok/s |
| 2(既定) | 56 | 2.754 | 10.120 | 19/20 | 1.40 tok/s |
| 3 | 80 | 3.285 | 15.038 | 18/20 | 0.94 tok/s |
| 4 | 104 | 5.245 | 28.666 | 11/20 | 0.81 tok/s |

ループを1回にすると、掛け算は20問中1問しか合わず、`964×59` に `55876`(正解は56876)と答えるような、桁の一部がずれた誤答が並んだ。
perplexityも英語で2.75から4.96、日本語で10.1から38.4に悪化した。
一方、3回・4回に増やしても良くはならず、4回では掛け算が11問まで落ち、`964×59` に `5684` と桁が欠けた答えを返した。
生成速度はループ回数にほぼ比例して遅くなった。
なお、2ループで1.40 tok/sという速度は、`causal_conv1d` を入れていないフォールバック実行での値である。

## 文章題とコードでも、1回だけが崩れた

「バットとボールで合計1.10ドル、バットはボールより1.00ドル高い」という問題では、ループ1回だけが式を正しく立てたうえで計算を誤った。

```
loops=1: The ball costs $0.15. If the ball is $x, the bat is $x + 1.00, and together they total $1.10, so 2x + 1.00 = 1.10 → x = 0.15.
loops=2: ... 2x + 1.00 = 1.10 \implies 2x = 0.10 \implies x = 0.05 ... The ball costs 5 cents.
```

「5台の機械が5分で5個作る」問題では、ループ1回は途中から `individual individual individual ...` と同じ単語を200トークンの上限まで繰り返した。
ループ2〜4回は、どれも `It would take **5 minutes**.` と正しく答えた。

Pythonの `fib(n)` を書かせると、ループ1回は `a = b` と `b = a + b` を別々の行に書いてしまい、正しく動かないコードになった。
ループ2〜4回は `a, b = b, a + b` の正しいコードを返した。

日本の首都を聞く質問だけは、1〜4回のすべてが `日本の首都は東京です。` と同じ答えだった。

面白かったのは「Sallyには兄弟が3人いて、兄弟はそれぞれ姉妹が2人いる。Sallyの姉妹は何人か」(正解は1人)という問題である。
ループ2〜4回はすべて「2人」と誤答した。
ループ1回だけが `Since Sally is one of those 2 sisters, she has 1 sister.` と正しく推論したが、`Wait, let me reconsider.` と同じ推論を繰り返して200トークンで打ち切られた。

## 考察: 回数を増やせば良いわけではない

READMEには「ループを3〜4回にすると最も性能が高い」という実験結果も載っている。
ただしこれは、学習時と推論時のループ回数をそろえて別々に学習したモデルの結果である。
今回のように2ループで学習された重みのまま推論時だけ回数を変えると、1回でも3回・4回でも性能は下がり、2回が最も良かった。
同じ重みを2回通すことが性能に効いていることは1回との比較ではっきり見えたが、それは学習時と同じ使い方をしたときの話で、推論時に回数を足せば賢くなるわけではなかった。

## まとめ

- SenseNova-Loop-9BのBF16版はgatedで、公式AWQ 4bit版はRTX 5060 Ti(16GB)で動いた。最大GPUメモリ確保量は8.28GiBだった。
- AWQ版はTransformers + gptqmodelで読むと埋め込み層とlm_headが読み込まれず、意味のない出力になった。2つを自分で逆量子化すると正常に答えた。
- ループ回数を2回(既定)から1回に減らすと、掛け算の正解が19/20から1/20に落ち、文章題・コードでも崩れた。
- 3回・4回に増やしても改善せず、4回では掛け算が11/20に下がった。速度はループ回数にほぼ比例して落ちた。

## 出典・ライセンス

- モデル: https://huggingface.co/sensenova/SenseNova-Loop-9B (Apache License 2.0)
- AWQ版: https://huggingface.co/sensenova/SenseNova-Loop-9B-AWQ (Apache License 2.0)
- コード: https://github.com/OpenSenseNova/SenseNova-Loop (Apache License 2.0)
- 検証ログ: https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-055
