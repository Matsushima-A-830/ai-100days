---
title: "「4GB GPUで8Bモデルを学習できる」というSoupの主張をRTX 5060 Tiで検証したら、学習は本当に動いたがアダプタが空だった"
emoji: "🍲"
type: "tech"
topics: ["ai", "llm", "pytorch", "finetuning", "gpu"]
published: true
---

## これは何

海外AIネタ100日チャレンジ Day 005。
今回取り上げるのは [Soup](https://github.com/MakazhanAlpamys/Soup)(Apache-2.0)。
「単一YAML + 1コマンドでLLMをファインチューニングできる」CLIで、目玉機能は**Layer Streaming**。
凍結したベースモデルの重みをVRAMに置かず、ホストRAMからデコーダ層を1層ずつGPUへ流し込むことで、**4GB GPUでも8Bモデルのファインチューニングができる**という主張をしています。

本家READMEのベンチマーク数値(RTX 3050 Laptop 4GB、119.6 tok/s、3.32GB peak)には、開発者自身によるこんな注記が付いています。

> measured on v0.72.2, before the v0.73.0 correctness repair that cost -4.8% at 32B; neither has
> been re-run on a 4 GB card since - re-measurement pending in issue #361

つまり**開発者自身が「今のバージョンではまだ4GBカードで再検証していない」と明言している状態**。
今回は、この再検証待ちの主張を、筆者のPCに載っているRTX 5060 Ti(16GB)を4GBに人為的に制限して追試しました。

:::message
この検証はクラウドの実装RoutineではなくGPUを持つローカルPC上で、人間(筆者)が直接動かしています。
CUDA GPUが前提の検証はクラウド実行環境では行えないため、今回は例外的な運用です。
:::

## 検証方法: Soup公式のColabノートブックを、もっと強いGPUで動かす

Soupのリポジトリには`notebooks/proof-4gb.ipynb`という「主張を自分で検証してみてください」というノートブックが公開されています。
Colabの無料T4(16GB)を`torch.cuda.set_per_process_memory_fraction`で4GBに制限し、

1. GPUのbf16対応確認
2. 4GBキャップが実際に機能するか
3. Layer Streamingしたモデルと通常モデルのフォワード出力が完全一致するか
4. 実際にLlama-3.1-8Bを4GB予算内で学習できるか

を順に確認する構成になっています。
今回はこの構成をそのまま踏襲し、Colab T4より強いRTX 5060 Ti(16GB、Blackwell)上で実行しました。

```bash
python3 -m venv ~/soup-venv && source ~/soup-venv/bin/activate
pip install 'huggingface-hub<1.32.0' 'soup-cli[train]==0.75.0'  # ノートブックが検証済みとして指定するバージョン
```

## 結果1: bit-exact性の確認は成立した

```
bf16 IN HARDWARE      True
capped at 4.00 GB  (fraction 0.234 of this card)
refused, as it should be: CUDA out of memory. Tried to allocate 4.29 GiB...

bit-exact (torch.equal): True
max abs diff:            0.0
```

4GBへのメモリキャップは実際に機能し、それを超える確保は正しく拒否されました。
そして本題である**「Layer Streamingで分割実行したモデルと、通常どおりVRAMに全部載せたモデルの出力が、浮動小数点ビットレベルで完全一致する」という主張**(`torch.equal`)も、実際にその通りの結果になりました。
最大絶対誤差は0.0。
小細工ではなく本当にビット単位で同じ計算をしていることが確認できました。

(余談: 筆者が最初に書いた比較コードはここで一度失敗しました。
Streaming用モデルの`state_dict()`を素朴に通常モデルへ`load_state_dict`しようとしたところ、ベース層の重みが実体を持たない**meta tensor**だったためにエラーになったのです。
Layer Streamingはフォワード時に層ごとに重みを動的ロードする設計なので、`state_dict()`には「実データ」ではなく「プレースホルダー」が入っている、ということに気づかされました。
これはこちら側の検証コードの誤りで、Soup自体の不具合ではありません。)

## 結果2: 8Bモデルの4GB学習は本当に動いた

いよいよ本題。
4GBにキャップしたプロセス内で、Llama-3.1-8B-Instruct(NousResearchの非ゲート配布版)をNF4量子化 + LoRA + Layer Streamingで実際に学習させました。

```yaml
base: NousResearch/Meta-Llama-3.1-8B-Instruct
training:
  quantization: 4bit
  stream_layers: true
  stream_buffers: 2
  stream_vram_override: 4000000000
  lora: { r: 8, alpha: 16 }
```

Soup自身が実行前に出す事前診断パネルが面白いので載せます。

```
base store   5.70 GB across 32 layers (pinned)
VRAM buffers 2 x 113 MB + 1 x 1051 MB large-layer slot = 1276 MB
peak VRAM    ~1.97 GB at batch 1 x seq 256 (logits 0.46 GB)
free VRAM    4.00 GB (training.stream_vram_override; driver reports 15.87 GB)
```

そして実測結果:

```
steps: 7  loss: 4.533 -> 4.073
peak VRAM allocated by this process: 1.78 GB
budget this process was capped to:   4.00 GB
```

**実測ピークVRAMは1.78GB**。
4GBの予算を大きく下回り、Soup自身の事前予測(1.97GB)にも近い値でした。
8Bモデル(bf16なら16GB超)が、本当に4GBを切る実メモリで学習できています。
lossも7ステップで4.533→4.073まで素直に下がっており、学習が実際に機能していることも確認できました。
**開発元の「4GB GPUで8Bモデルを学習できる」という主張は、計算量・メモリ使用量の面ではこのRTX 5060 Ti上でも再現できた**と言えます。

## 結果3: でも、保存されたLoRAアダプタファイルが空だった

ここで想定外のことが起きました。
学習後に生成された`out-8b/adapter_model.safetensors`を`safetensors`ライブラリで直接開いてみたところ、**テンソルが0個**(ファイルサイズ40バイト、ヘッダーのみ)でした。

```python
from safetensors import safe_open
with safe_open('out-8b/adapter_model.safetensors', framework='pt') as f:
    print(len(list(f.keys())))  # -> 0
```

学習中に保存された`checkpoint-7/adapter_model.safetensors`も同じく0個。
一方で`checkpoint-7/optimizer.pt`は13.7MBあり、ログに出ていた`LoRA applied: 3,407,872 trainable`(約340万パラメータ)というオプティマイザの状態量としては規模感が一致しています。
つまり**学習そのもの(勾配計算・loss低下)は確かに起きているのに、学習済みのLoRA重みがファイルとして正しく保存されていない**ということです。

8Bモデルでの再現は時間がかかるため、同じ経路を高速なSmolLM2-135M-Instructで再現し(`debug_empty_adapter.py`)、学習直後のモデルを3つの方法で覗いてみたところ、原因が見えてきました。

```
model.state_dict()                    -> ...layers.0.self_attn.q_proj.lora_A.default.weight   (inner無し、値は非ゼロ)
model.named_parameters()              -> ...layers.0.inner.self_attn.q_proj.lora_A.default.weight  (inner有り)
peft.get_peft_model_state_dict(model) -> 0 keys
```

Soupは、Layer Streaming用にラップした各デコーダ層(`StreamedDecoderLayer`)の`state_dict()`を独自に上書きし、保存時のキーからラッパー固有の`inner.`プレフィックスを取り除いています(ソースコードのコメントいわく「普通のLoRAアダプタと見分けがつかない形で保存する」ための意図的な設計)。

ところがこの上書きは`state_dict()`にしか適用されておらず、PyTorch標準の`named_parameters()`は`inner.`付きのまま。
Hugging Face `Trainer.save_model()` → `PeftModel.save_pretrained()`が内部で呼ぶ`peft.get_peft_model_state_dict()`は、`named_parameters()`ベースでLoRAキーを特定してから`state_dict()`と突き合わせる実装になっているため、**キー名が一致せず「該当パラメータなし」と判断され、エラーも警告も出さずに空のdictを返してしまう**のです。
これがそのまま`adapter_model.safetensors`に書き込まれ、0テンソルのファイルになっていました。

学習自体(勾配計算・loss低下)が正常だったのは、この不一致がフォワード/バックワードパスには一切影響しないから。
135Mモデルでも8Bモデルでも同じ現象が再現したので、モデルの種類に依存しない、Layer Streaming機能自体に起因する不具合と見ています。

**回避策も確認できました。**
`trainer.save_model()`を経由せず、`model.state_dict()`(Soup独自の上書き版。キーは正しく、値も実際に学習済み)から`"lora_" in key`で直接フィルタして`safetensors.save_file()`で保存すればOKです。

```python
sd = model.state_dict()
lora_sd = {k: v.clone().cpu() for k, v in sd.items() if "lora_" in k}
from safetensors.torch import save_file
save_file(lora_sd, "adapter_model.safetensors")
```

SmolLM2-135Mで実際にこの方法を試したところ、120個のテンソルが正しく保存・再読み込みでき、学習済みの非ゼロ値(例: `max_abs=0.0417`)も確認できました。

(再現コード一式は[experiments/day-005/](https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-005)に置いてあります。)

## まとめ

| 項目 | 結果 |
|---|---|
| bf16ハードウェア対応確認 | ✓ |
| 4GBメモリキャップの強制 | ✓ |
| streamed/resident フォワード出力のbit-exact一致 | ✓ |
| 8Bモデルを4GB予算内で学習 | ✓(peak 1.78GB) |
| 学習済みLoRAアダプタの保存 | ✗(空ファイル) |
| 不具合の原因特定 | ✓(state_dict()とnamed_parameters()のキー不一致) |
| 回避策 | ✓(state_dict()から直接lora_キーを抽出、動作確認済み) |

「4GB GPUで8Bモデルを学習できる」という開発元の主張は、**計算・メモリの面では本当に成立していました**。
Layer Streamingという技術自体の正しさ(streamed/residentのbit-exact一致)も実測で確認できています。
ただ、今回ぶつかったのは「動いた」の先、「学習済みモデルを実際に持ち帰れるか」という部分の問題でした。
原因はPEFTの`get_peft_model_state_dict()`とSoup独自の`state_dict()`上書きとのキー名不一致で、回避策(state_dict()から直接抽出)も動作確認できたので、最終的には「使える学習済みモデルを実際に持ち帰る」ところまで到達できました。
派手な主張ほど、末端(保存・永続化)まで含めて検証する価値があるという、地味だけど実用上大事な教訓でした。

## ライセンス・出典

- コード: [github.com/MakazhanAlpamys/Soup](https://github.com/MakazhanAlpamys/Soup)(Apache-2.0)
- 検証用ベースモデル: [NousResearch/Meta-Llama-3.1-8B-Instruct](https://huggingface.co/NousResearch/Meta-Llama-3.1-8B-Instruct)(Llama 3.1 Community License)
- 比較用小型モデル: [HuggingFaceTB/SmolLM2-135M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct)(Apache-2.0)
