# Day 037: SJTU-DENG-Lab/WaveForcing

## 対象

- コード: https://github.com/SJTU-DENG-Lab/WaveForcing (Apache-2.0。`training/`配下のみ別ライセンス)
- 論文: https://huggingface.co/papers/2611.00859 (arXiv:2611.00859)
- 学習済み重み: https://huggingface.co/SJTU-DENG-Lab/WaveForcing-1.3B (`4step/` / `5step/`)
- プロジェクトページ: https://sjtu-deng-lab.github.io/WaveForcing/

Wan2.1-T2V-1.3Bをベースに、チャンク単位の因果アテンション(Wave Forcing)と専用の推論ランタイム
(WaveRT)でストリーミング動画生成を高速化する手法。詳細は`results.md`、記事本体
(`articles/day-037-wave-forcing-streaming-video.md`)を参照。

## このRoutineでやったこと

1. リポジトリを実際にcloneし、`LICENSE`・`README.md`・`wave_rt/config.py`・`pyproject.toml`を読んで、
   ライセンス・ハードウェア要件・クイックスタート手順を確認した。
2. このRoutine実行環境に`nvidia-smi`もCUDA対応の`torch`も存在しないことを確認した(`results.md`参照)。
3. README記載のクイックスタートが8GPU(Hopperクラス)構成を前提にしていることを確認し、
   このRoutine実行環境では推論自体を実行できないと判断してローカル検証にエスカレーションする。

## ローカル検証の再現手順(人間向け)

GPU(できればHopperアーキテクチャ・H100/H200クラス)を用意し、以下をそのまま実行する手順が
upstreamのREADMEに記載されている。

```bash
# 1. 依存関係(リポジトリルートで)
# Python 3.12 / torch==2.11.0+cu128 が前提。pyproject.tomlのuv.sources経由で
# https://download.pytorch.org/whl/cu128 からインストールされる。
uv sync   # もしくは pip install -e . 相当

# 2. ベースモデルとWaveForcing-1.3Bの重みを取得
python -m pip install -U "huggingface_hub[cli]"

hf download Wan-AI/Wan2.1-T2V-1.3B-Diffusers \
  --local-dir ckpts/Wan2.1-T2V-1.3B-Diffusers

hf download SJTU-DENG-Lab/WaveForcing-1.3B \
  --local-dir ckpts/WaveForcing-1.3B

# 3. WaveRTを起動(5-step・8GPU・5+2構成、README記載のクイックスタートそのまま)
python -m wave_rt \
  --model-path ckpts/Wan2.1-T2V-1.3B-Diffusers \
  --gen-ckpt ckpts/WaveForcing-1.3B/5step/model.safetensors \
  --rf-step 5 \
  --wp-size 6 \
  --denoising-step-list 1000,800,600,400,200 \
  --num-frames 24 \
  --height 480 \
  --width 832 \
  --vae-stages 2 \
  --vae-partition time \
  --kv-context causal \
  --exchange-mode paged \
  --attention-backend torch_sdpa \
  --cuda-visible-devices 0,1,2,3,4,5,6,7 \
  --prompt "A cinematic shot of a fluffy corgi running on a sunny beach, waves in the background." \
  --task quickstart \
  --run-tag corgi

# 出力: outputs/quickstart/corgi/video.mp4, outputs/quickstart/corgi/metrics.json
```

4-stepチェックポイント(README記載の「-134.8 E2E FPS」の構成)で試す場合は、
`--gen-ckpt`を`ckpts/WaveForcing-1.3B/4step/model.safetensors`に変え、
`--rf-step 4 --wp-size 5 --denoising-step-list 1000,750,500,250 --vae-stages 3`に差し替える。

**注意: 上記はGPU 8基(Hopperクラス)前提の構成。** 8基のH100/H200級GPUを用意できない場合、
`wp_size`を減らす(例: 単一GPU相当まで落とす)と`rf_step`も連動して小さくなり、Wave Forcing本来の
チャンク単位パイプライン化はほぼ機能しない退化的な構成になる点に注意。手元のGPU数・VRAM量に応じて、
まずは`--num-frames`を小さくした短い生成が通るかどうかから試すのが安全。

## ローカル検証(実施済み・2026-11-04)

**上記の手順は、GPU基数とは無関係に、現時点ではそのまま実行できない。** `uv sync`はPyPI公開版の
`sglang`を一切インストールしない(`pyproject.toml`のコメントが参照する`sgl-dlab`という非公開フォーク
がどこにもリンクされていない)。公開版`sglang`を別途インストールしても、`wave_rt`が要求する
`WanRollingForcingPipeline`というパイプラインクラスがそのパッケージのレジストリに存在せず、
`ValueError: Pipeline class 'WanRollingForcingPipeline' not found in registry`で失敗する。
単一GPU向けの比較スクリプト`scripts/wrt_ref_single.py`も同じ理由で動かない(加えて公開版sglangとの
APIの食い違いもある)。詳細な再現ログは`results.md`の「4. ローカル検証」を参照。
