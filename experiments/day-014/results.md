# Day 014 — TokenRouter(thu-nics) 検証結果

**結論: Routine実行環境の制約(CUDA GPUが存在しない)およびライセンス表記の不備により、
実際のルーティング/スループット検証には進めなかった。ローカル検証待ち。**

出典: https://github.com/thu-nics/TokenRouter (Hugging Face Daily Papers 2026-10-09掲載)

## 1. ライセンス確認(検証開始前のチェック)

CLAUDE.md・today.mdの指示に従い、検証に着手する前にリポジトリのライセンス表記を確認した。

```
$ git clone --depth 1 https://github.com/thu-nics/TokenRouter /tmp/tokenrouter-license-check
$ find /tmp/tokenrouter-license-check -maxdepth 1 -type f
./.gitignore
./README.md
./pyproject.toml
$ find /tmp/tokenrouter-license-check -iname "*licen*" -o -iname "*copying*" -o -iname "*notice*"
(該当ファイルなし)
```

- リポジトリルートに **LICENSE/COPYING/NOTICEファイルは存在しない**(0件)。
- `pyproject.toml` の `classifiers` には以下の記載のみある:
  ```
  classifiers = [
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: Apache Software License",
  ]
  ```
  → Apache License 2.0を示唆する分類タグはあるが、ライセンス全文ファイルが同梱されておらず、
  README本文にもライセンスへの言及が一切ない。
- GitHub APIでのリポジトリ側のライセンス自動検出結果も確認を試みたが、本セッションのGitHubアクセス範囲が
  `matsushima-a-830/ai-100days` に限定されているため `api.github.com` 経由での取得はできなかった
  (`git clone` 自体は認証不要の公開リポジトリとして成功している)。

**→ CLAUDE.md「ライセンスを確認する」today.md「不明なまま記事化・コード転載をしないこと」に従い、
ライセンスが確定しない状態でのコード転載・記事化は行わない。**

## 2. GPU要否の確認

today.mdの指示に従い、まずRoutineのクラウド実行環境にCUDA GPUがあるかを確認した。

```
$ nvidia-smi
bash: nvidia-smi: command not found
$ ls /dev/nvidia*
ls: cannot access '/dev/nvidia*': No such file or directory
$ python3 -c "import torch; print(torch.cuda.is_available())"
ModuleNotFoundError: No module named 'torch'
```

→ 本Routine実行環境には **GPUデバイス自体が存在しない**(nvidia-smiコマンド無し、`/dev/nvidia*`無し)。

次に、小型モデル同士(0.6B+1.7B程度)の最小構成で動かせないかをリポジトリ内で確認した。

- `config/` 配下の5種類の設定例(r2r, citer, collm, rstitch, me)はすべて large側に
  `Qwen/Qwen3-32B`、small側に `Qwen/Qwen3-0.6B` を使用しており、**「1.7B」を含む設定例はリポジトリ全体で0件**。
- README「Reproducing Our Results」節に以下の記載があり、**CUDA MPS(複数モデルが同一物理GPUを共有する場合に推奨)が前提**:
  ```
  ### 1. Launch CUDA MPS
  If multiple models share the same physical GPU, CUDA MPS is recommended for
  reproducing overlapping serving behavior and improving concurrent scheduling performance.
  export CUDA_MPS_PIPE_DIRECTORY=...
  nvidia-cuda-mps-control -d
  ```
- Qwen3-32B側の設定は `tp_size: 2`(テンソル並列2)を指定しており、複数GPU構成が前提。
- `pyproject.toml` の依存関係には `sglang`, `sgl-kernel`, `flashinfer-python`, `cuda-python`, `nvidia-ml-py`, `nvtx`
  が含まれ、いずれもNVIDIA CUDA専用のライブラリ・推論エンジンである(CPU/Apple Siliconでは動作不可)。
- 各configは `base_gpu_id`, `disable_cuda_graph`, `cuda_graph_bs_extend` などCUDA Graph関連パラメータを必須項目として持つ。
- `model_path` はYAML上は単純な文字列パラメータなので理論上は別モデルへの差し替えは可能だが、各ルーティング手法
  (R2R/CITER/Co-LLM等)は特定のモデルペア(0.6B+32Bなど)向けに学習済みのルーター重み(Hugging Face上の
  `nics-efc/...`)を使う前提になっており、モデルを軽量なものに差し替えるとルーターの再学習が必要になる可能性が高い。
  公式にサポートされた軽量構成は存在しない。

**→ 公式のサンプル構成はGPU(できれば複数GPU)が実質必須であり、本Routineのクラウド実行環境ではハードウェアが
存在しないため、インストール・実行のいずれも試せなかった。** `sgl-kernel`/`flashinfer-python`等の大容量CUDA依存
パッケージのインストールを試みることも検討したが、GPUデバイスが無い時点で実行(推論)が成立しないことが明らかな
ため、不要なダウンロード・ディスク消費を避けてここで判断を止めた。

## 3. 判断

CLAUDE.mdの「判断に迷う場合は、先にローカルで再現するかを確認してから分類する」に従い、以下の2点は
Routine環境の制約なのかツール自体の性質なのかを断定せずローカル検証にエスカレーションする。

- **ライセンス**: リポジトリ側のLICENSEファイル欠落は環境に依らない事実だが、これが「未整備なだけで実質Apache」なのか、
  著者に確認が必要なのかは人間の判断が必要。
- **GPU要件**: 本Routine環境にGPUが無いことは確認済みだが、matsu氏のローカルPCにCUDA GPUがあるかは不明。
  ローカルにGPUがあれば、小型モデル同士の構成を自作して試す、または公式のQwen3-0.6B+32B構成を
  (リソースが足りる範囲で)試すことで、「ツール自体の既定構成がGPU前提」という検証に直接関係する知見として
  記事化できる可能性がある。ローカルでもGPUが無い/足りない場合は、それ自体が「人間のローカルPCのスペックが
  足りず動かなかった」という検証に直接関係する失敗として記事化できる。

現時点では記事・X投稿案・note原稿・シェアカードは作成していない(実際に動かしていないものを
「動いた」として書かないため)。ローカル検証の結果が出た段階で、本ディレクトリに結果を追記し、
記事等を作成する。
