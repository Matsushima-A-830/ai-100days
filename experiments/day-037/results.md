# Day 037 検証結果: SJTU-DENG-Lab/WaveForcing

検証日: 2026-11-04
検証対象: https://github.com/SJTU-DENG-Lab/WaveForcing (HEAD時点でclone・確認、Apache-2.0)
論文: https://huggingface.co/papers/2611.00859 (arXiv:2611.00859)
モデル重み: https://huggingface.co/SJTU-DENG-Lab/WaveForcing-1.3B
プロジェクトページ: https://sjtu-deng-lab.github.io/WaveForcing/

## 1. 確認できたこと

### 1-1. ライセンス

リポジトリを実際にcloneして`LICENSE`ファイルの内容をそのまま確認した。

- 推論コード本体(`wave_rt/`, `naive_rt/`): **Apache License 2.0**(リポジトリルートの`LICENSE`)。
- `training/`配下の参考実装(RollingForcingベースのトレーナー)のみ、別ライセンス
  (`training/LICENSE`、academic-use license)が適用される。README本文にも明記されている。

### 1-2. クイックスタート手順とハードウェア要件

`README.md`を実際に読み、推論を動かすための要件を確認した。

- Python 3.12、PyTorch 2.11.0+cu128、SGLangのdiffusion runtime、**Hopperアーキテクチャ(H100/H200クラス)
  のGPU**が前提(`pyproject.toml`にcu128ビルドのtorchが固定されている)。
- README記載のQuick Startは「WaveForcing-1.3B・5-step・8GPU構成(5+2: 5 denoisingステージ+1 clean-KV store
  rank+2 streaming VAEステージ)」が最小単位として示されている。
- `wave_rt/config.py`を読むと、`rf_step + 1 == wp_size`という制約があり(`wp_size`はWaveRTの並列度)、
  技術的には`wp_size=1`(実質1プロセス)も値としては許容されるが、その場合`rf_step=0`になり、
  論文が提案する「チャンク単位の因果アテンションによるパイプライン化」という手法そのものが機能しない
  退化的な設定になる。つまり、この手法の効果を実際に体感できる構成には複数GPU(論文の実験は8×H200)
  が前提になっている。

### 1-3. 論文・READMEが報告している数値(筆者自身の実測ではない)

READMEの「Current results」表に記載されている、著者らの実測値(8×NVIDIA H200、832×480、
399 latent frames=1593 decoded frames):

| モデル | ステップ数 | 構成 | Steady FPS (p50) | E2E FPS |
|---|---:|---|---:|---:|
| WaveForcing-1.3B | 4 | 4+3・BF16/FA3 | 152.1 | **134.8** |
| WaveForcing-1.3B | 5 | 5+2・BF16/FA3 | 99.6 | 96.5 |

比較対象として示されている単一GPUベースラインは**19.06 FPS**で、8×H200構成の134.8 FPSは
**7.07倍**に相当する(いずれもREADMEに明記された著者らの報告値)。

## 2. 実行環境の確認(このRoutine実行環境でできたこと)

```
$ nvidia-smi
bash: nvidia-smi: command not found
$ python3 -c "import torch; print(torch.cuda.is_available())"
ModuleNotFoundError: No module named 'torch'
```

GPUなし・CUDA環境なしであることを確認した。

## 3. ローカル検証へのエスカレーション

Wave Forcing/WaveRTは動画拡散モデルの推論であり、READMEのQuick Start・`wave_rt/config.py`の制約から
判断して、手法の効果を再現するには複数基(著者らは8基)のHopperクラスGPUが前提になっている。
これはツール自体の性質(動画拡散モデル+マルチGPUパイプライン並列という設計)であり、GPUを持たない
実行環境固有の制約である。Routine環境の制約により実機推論は未検証、ローカル検証待ち。
再現コマンドは`README.md`参照。
