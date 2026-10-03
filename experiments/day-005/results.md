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
起きている。Layer Streaming + 4bit量子化 + LoRA保存の組み合わせに固有の問題である可能性があり、
再現性のある具体的な不具合として記録しておく(本記事の検証範囲では原因の特定までは行っていない)。

## まとめ

| 項目 | 結果 |
|---|---|
| bf16ハードウェア対応 | ✓ (RTX 5060 Tiはネイティブ対応) |
| 4GBメモリキャップの強制 | ✓ (超過確保を正しく拒否) |
| streamed/resident フォワード出力のbit-exact一致 | ✓ (torch.equal = True) |
| 8Bモデルを4GB予算内で学習 | ✓ (peak VRAM 1.78GB < 4GB) |
| 学習によるloss低下 | ✓ (4.533 → 4.073、7ステップ) |
| 学習済みLoRAアダプタの保存 | ✗ (adapter_model.safetensorsが空、0テンソル) |

「4GB GPUで8Bモデルを学習できる」という開発元の主張は、計算量・メモリ使用量の面では
このRTX 5060 Ti上でも再現できた。しかし今回使った条件(4bit量子化 + Layer Streaming + LoRA)では、
学習済みの成果物(アダプタの重み)がファイルとして正しく永続化されない、という
別の問題に実際にぶつかった。「動いた」のは学習プロセスまでで、「使える学習済みモデルが手に入った」
とまでは言えない、というのが今回の正直な結論。
