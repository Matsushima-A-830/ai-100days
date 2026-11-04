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

## 3. ローカル検証へのエスカレーション(Routine時点の判断)

Wave Forcing/WaveRTは動画拡散モデルの推論であり、READMEのQuick Start・`wave_rt/config.py`の制約から
判断して、手法の効果を再現するには複数基(著者らは8基)のHopperクラスGPUが前提になっている。
これはツール自体の性質(動画拡散モデル+マルチGPUパイプライン並列という設計)であり、GPUを持たない
実行環境固有の制約である。Routine環境の制約により実機推論は未検証、ローカル検証待ち。
再現コマンドは`README.md`参照。

## 4. ローカル検証(人間のGPU環境、2026-11-04)

人間のPC(RTX 5060 Ti, 16GB VRAM、WSL2)で実際にインストール・実行を試みたところ、GPU基数の
問題より手前で**この手法の核心となるパイプラインクラス自体が、公開されている依存関係の中に存在しない**
ことが分かった。GPUが8基あっても同じ場所で失敗する、ツール自体の問題である。

### 4-1. `uv sync`はPyPI公開のsglangを依存関係に含めていない

```bash
$ cd WaveForcing && uv sync
# torch==2.11.0+cu128 等は入るが、sglangは一切インストールされない
$ .venv/bin/python -c "import sglang"
ModuleNotFoundError: No module named 'sglang'
```

`pyproject.toml`のコメントには「`uv pip install -e sgl-dlab/python[diffusion]`で編集可能インストール
する」という記述があるが、`sgl-dlab`というディレクトリ・パッケージはこのリポジトリのどこにも存在せず、
READMEにも入手方法の説明がない。つまり、公式クイックスタートに書かれているコマンドだけでは、
WaveRTが依存する実行基盤そのものが手に入らない。

### 4-2. PyPI公開版のsglangを後から入れても、専用パイプラインクラスが無い

公開されている`sglang`(0.5.23 / 0.5.9の両方で確認)を`uv pip install sglang[diffusion]`で追加して、
`wave_rt/config.py`が既定で要求する`pipeline_class_name = "WanRollingForcingPipeline"`を実際に
ロードしようとすると、次のように失敗する。

```
$ .venv/bin/python -c "
from sglang.multimodal_gen.runtime.pipelines_core import build_pipeline
...(ServerArgsをwave_rt/config.py相当の値で構築)...
build_pipeline(sa)
"
[rank0]: ValueError: Pipeline class 'WanRollingForcingPipeline' not found in registry.
Available pipelines: ['ComfyUIFluxPipeline', ..., 'WanCausalDMDPipeline', 'WanDMDPipeline',
'WanImageToVideoDmdPipeline', 'WanImageToVideoPipeline', 'WanPipeline', 'ZImagePipeline']
```

リポジトリ全体を`grep -rl 'RollingForcing'`しても、`wave_rt/config.py`のデフォルト文字列以外に
`RollingForcing`という名前は一度も出てこない。公開版`sglang`のソース全体にも同じ文字列は一度も
出てこない。つまり`WanRollingForcingPipeline`は、著者らの非公開フォーク(`sgl-dlab`)にのみ存在する
クラスで、公開されているコードだけでは原理的に組み立てられない。

### 4-3. README記載の「単一GPUベースライン」比較スクリプトも同じ理由で動かない

READMEが示す19.06 FPSの単一GPU比較に対応する`scripts/wrt_ref_single.py`も、同じ
`WanRollingForcingPipeline`を要求する作りになっており、さらに公開版sglangとの間にAPIの食い違いも
見つかった。

```
$ .venv/bin/python scripts/wrt_ref_single.py --num-frames 6 --out /tmp/wf-out
TypeError: maybe_init_distributed_environment_and_model_parallel() got an
unexpected keyword argument 'cfg_degree'
```

実際の関数シグネチャは`enable_cfg_parallel: bool`であり、`cfg_degree`という引数は存在しない
(`inspect.signature`で確認)。この食い違いを手で修正してから再実行すると、今度は4-2と同じ
`WanRollingForcingPipeline not found in registry`で止まる。つまりこの比較スクリプトも、
API不一致を直してもなお、同じ根本原因で完走しない。

### 4-4. まとめ

- GPUが8基(Hopperクラス)用意できたとしても、現状公開されている依存関係だけではこの手法の核心
  (`WanRollingForcingPipeline`)を動かすことができない。これは「GPUが足りない」という
  Routine実行環境固有の制約ではなく、**リポジトリと依存関係(sglangの非公開フォーク)の公開範囲の
  不一致**という、ツール自体に直接関係する不具合である。
- `pyproject.toml`のコメントが参照する`sgl-dlab`フォークは、このリポジトリのどこにもリンク・説明
  されておらず、現時点では第三者が再現する手段がない。
- モデルの重み(Wan2.1-T2V-1.3B・WaveForcing-1.3B)自体はHugging Faceで公開されており、ダウンロード
  可能であることは確認した(ダウンロード自体は試みたが、上記の理由で推論まで進めても意味がないため、
  モデル取得は完了させていない)。
