# Day 005 検証結果

実行日: 2026-10-03。実行環境: ローカルPC、NVIDIA GeForce RTX 5060 Ti(16GB VRAM、sm_120 / Blackwell)、
WSL2 Ubuntu、`soup-cli==0.75.0`、`torch==2.11.0+cu128`、`transformers==5.18.0`、`peft==0.21.2`、
`bitsandbytes==0.50.2`。

## Section 1-4: 基盤的な主張の確認(すべて成立)

```
GPU                   NVIDIA GeForce RTX 5060 Ti  (sm_120)
VRAM                  17.1 GB
bf16, incl. emulation True
bf16 IN HARDWARE      True
Soup will train in    bf16

capped at 4.00 GB  (fraction 0.234 of this card)
refused, as it should be: CUDA out of memory. Tried to allocate 4.29 GiB. GPU 0 has a total capacity of 15.93 GiB of

bit-exact (torch.equal): True
max abs diff:            0.0
```

- 4GBへのメモリキャップは実際に機能し、超過確保は正しく拒否された。
- **Layer Streamingで分割実行したモデルと通常のレジデントモデルのフォワード出力が、浮動小数点ビットレベルで完全一致**
  (`torch.equal` = True、最大絶対誤差 0.0)。開発元の「streamed == resident, bit for bit」という主張は
  SmolLM2-135M-Instructで実際に成立することを確認した。

(全ログ: `run2-sections1to4.log`。初回実行`run1-sections1to4.log`では自作の比較コードの誤り
(=streamedモデルのベース層はmetaテンソルでload_state_dictできない)でエラーになったが、
これはこちらのスクリプトの実装ミスで、Soup自体の不具合ではない。修正して再実行し上記の結果を得た。)

## Section 5: Llama-3.1-8Bを4GBキャップ下で実際に学習

```yaml
base: NousResearch/Meta-Llama-3.1-8B-Instruct
training:
  quantization: 4bit
  stream_layers: true
  stream_buffers: 2
  stream_vram_override: 4000000000
  lora: { r: 8, alpha: 16 }
```

Soup自身の事前診断パネル(実行ログより):

```
base store   5.70 GB across 32 layers (pinned)
VRAM buffers 2 x 113 MB + 1 x 1051 MB large-layer slot = 1276 MB
peak VRAM    ~1.97 GB at batch 1 x seq 256 (logits 0.46 GB)
free VRAM    4.00 GB (training.stream_vram_override; driver reports 15.87 GB)
```

実測結果:

```
steps: 7  loss: 4.533 -> 4.073
peak VRAM allocated by this process: 1.78 GB
budget this process was capped to:   4.00 GB
```

**headline主張(8Bモデルを4GB未満で学習できる)は、このRTX 5060 Ti上でも成立した。**
実測ピークVRAM 1.78GBは4GBの予算を大きく下回り、Soup自身の事前予測(~1.97GB)にも近い。
7ステップの学習でlossが4.533→4.073まで一貫して低下しており、学習自体が実際に機能していることも確認できた。

## 見つかった問題: 保存されたLoRAアダプタファイルが空

学習完了後に生成された`out-8b/adapter_model.safetensors`(最終出力)と
`out-8b/checkpoint-7/adapter_model.safetensors`(学習中チェックポイント)の両方を
`safetensors`で直接読み込んで確認したところ、**どちらもテンソルが0個(ファイルサイズ40バイト、ヘッダーのみ)**だった。

```python
from safetensors import safe_open
with safe_open('out-8b/adapter_model.safetensors', framework='pt') as f:
    print(len(list(f.keys())))  # -> 0
```

一方で`out-8b/checkpoint-7/optimizer.pt`は13.7MBあり、`LoRA applied: 3,407,872 trainable / 8,030,261,248 total`
というログの通り、約340万パラメータ分のオプティマイザ状態が存在することと整合する規模感だった。
つまり**学習自体は(lossの低下からも)実際に起きているが、学習済みのLoRA重みがディスクに正しく保存されていない**。

これは筆者が自作した比較コードの不備ではなく、`soup train`本体の保存処理(`wrapper.train()`内のアダプタ保存)で
起きている。

## 根本原因の特定: state_dict()とnamed_parameters()のキー不一致

8Bモデルでの再現には時間がかかるため、同じ経路(`stream_layers: true`)を高速な
SmolLM2-135M-Instructで再現し(`debug_empty_adapter.py`)、学習直後のモデルを3つの異なる方法で
調べたところ、キーの付け方に不一致があることがわかった。

```
model.state_dict()                    -> ...layers.0.self_attn.q_proj.lora_A.default.weight   (inner無し、値は非ゼロ)
model.named_parameters()              -> ...layers.0.inner.self_attn.q_proj.lora_A.default.weight  (inner有り)
peft.get_peft_model_state_dict(model) -> 0 keys
```

Soupは、Layer Streaming用にラップした各デコーダ層(`StreamedDecoderLayer`、
`soup_cli/utils/layer_stream_runtime.py`)の`state_dict()`を独自に上書きし、保存時のキーから
`inner.`というラッパー固有のプレフィックスを取り除いている(ソースコードのコメントによれば、
「普通のLoRAアダプタと見分けがつかない形で保存する」ための意図的な設計)。

しかしこの上書きは`state_dict()`にしか適用されておらず、`named_parameters()`(PyTorch標準メソッド)
は`inner.`付きのままである。Hugging Face `Trainer.save_model()` -> `PeftModel.save_pretrained()`が
内部で呼ぶ`peft.get_peft_model_state_dict()`は、`named_parameters()`ベースでLoRAキーを特定してから
`state_dict()`と突き合わせる実装になっているため、キー名の不一致により**該当パラメータが1つも
見つからず、エラーも警告も出さずに空のdictを返す**。これがそのまま`adapter_model.safetensors`に
書き込まれ、0テンソルのファイルになっていた。

学習自体(勾配計算・loss低下)が正常だったのは、この不一致がフォワード/バックワードパスには
一切影響せず、保存経路だけが壊れているため。135Mモデルでも8Bモデルでも同じ現象が再現したことから、
モデルアーキテクチャに依存しない、Layer Streaming機能自体に起因する不具合と考えられる。

### 回避策(動作確認済み)

`trainer.save_model()`(内部で`get_peft_model_state_dict()`を使う)を経由せず、
`model.state_dict()`(Soup独自の上書き版、キーは正しく値も実際に学習済み)から
`"lora_" in key`で直接フィルタして`safetensors.save_file()`で保存すれば、正しいLoRA重みが取れる。

```python
sd = model.state_dict()
lora_sd = {k: v.clone().cpu() for k, v in sd.items() if "lora_" in k}
from safetensors.torch import save_file
save_file(lora_sd, "adapter_model.safetensors")
```

SmolLM2-135Mで実際にこの方法を試したところ、120個のテンソルが正しく保存・再読み込みでき、
学習済みの非ゼロ値(例: `max_abs=0.0417`)も確認できた。再現コード: `debug_empty_adapter.py`。

## まとめ

| 項目 | 結果 |
|---|---|
| bf16ハードウェア対応 | ✓ (RTX 5060 Tiはネイティブ対応) |
| 4GBメモリキャップの強制 | ✓ (超過確保を正しく拒否) |
| streamed/resident フォワード出力のbit-exact一致 | ✓ (torch.equal = True) |
| 8Bモデルを4GB予算内で学習 | ✓ (peak VRAM 1.78GB < 4GB) |
| 学習によるloss低下 | ✓ (4.533 → 4.073、7ステップ) |
| 学習済みLoRAアダプタの保存 | ✗ (adapter_model.safetensorsが空、0テンソル) |
| 不具合の原因特定 | ✓ (state_dict()とnamed_parameters()のキー不一致、135M/8B両方で再現) |
| 回避策 | ✓ (model.state_dict()からlora_キーを直接抽出して保存、動作確認済み) |

「4GB GPUで8Bモデルを学習できる」という開発元の主張は、計算量・メモリ使用量の面では
このRTX 5060 Ti上でも再現できた。しかし今回使った条件(4bit量子化 + Layer Streaming + LoRA)では、
学習済みの成果物(アダプタの重み)がファイルとして正しく永続化されない、という別の問題に実際に
ぶつかった。原因は`StreamedDecoderLayer.state_dict()`の独自上書きと`named_parameters()`の
キー不一致で、PEFTの`get_peft_model_state_dict()`が黙って空のdictを返すこと。回避策(state_dict()
から直接lora_キーを抽出)も動作確認できたので、「動いた」で終わらず「使える学習済みモデルを
実際に持ち帰る」ところまで到達できた。
