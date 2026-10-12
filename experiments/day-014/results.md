# Day 014 — TokenRouter(thu-nics) 検証結果

**結論: Routine実行環境の制約(CUDA GPUが存在しない)およびライセンス表記の不備により、
実際のルーティング/スループット検証には進めなかった。人間がローカルPC(RTX 5060 Ti, 16GB)で
検証した結果、ライセンス不備は再確認、GPU面では新たに「ハードウェア世代の非対応」という
別種のブロッカーが判明した(詳細は末尾の追記セクション)。**

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

## 4. 追記(2026-10-12、人間のローカルPCでの検証結果)

### 4-1. ライセンス: GitHub自身の自動検出でも「不明」を再確認

GitHub REST APIの `license` フィールドを直接確認した。

```
$ gh api repos/thu-nics/TokenRouter | jq .license
null
```

GitHub自身のライセンス自動検出機構(有名なLICENSEファイルパターンやSPDX識別子を認識する仕組み)でも
`null`(未検出)という結果だった。`pyproject.toml`のclassifierにApacheの記載がある以外、確定的な
ライセンス表記はリポジトリ内に存在しないことを、Routineとは独立した経路で再確認した形になる。
**→ ライセンスは依然として未確定。著者への確認を推奨する状態に変わりはない。**

### 4-2. GPU: 「GPUが無い」から「GPUの世代が新しすぎて対応していない」に問題が変わった

ローカルPC(NVIDIA GeForce RTX 5060 Ti, 16GB VRAM, Blackwell世代 / Compute Capability sm_120、
Driver 591.86)で、実際に環境構築とサーバー起動を試みた。

```bash
git clone https://github.com/thu-nics/TokenRouter
cd TokenRouter
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

`pyproject.toml`が指定する `torch==2.8.0`・`sglang==0.5.1`・`sgl-kernel==0.3.8`・
`flashinfer-python==0.2.11.post3`・`cuda-python` を含む全依存関係のインストールは**成功した**
(exit code 0)。torchも`torch.cuda.is_available()`でRTX 5060 Tiを正しく認識した
(`torch-2.8.0+cu128`、`capability: (12, 0)`)。

公式configが要求するQwen3-32B(tp_size=2、複数GPU)は16GB・GPU1枚のこの環境では原理的に
不可能なため、代わりに軽量なQwen3-0.6B単体で `sglang.launch_server` を実際に起動し、
推論サーバーとしての基本動作を確認した。

```bash
python3 -m sglang.launch_server --model-path Qwen/Qwen3-0.6B --port 30001 \
  --mem-fraction-static 0.5 --disable-cuda-graph
```

サーバーは正常に起動し、モデルの重みも正しくGPUにロードされた。

```
[2026-10-12 11:25:04] Load weight end. type=Qwen3ForCausalLM, dtype=torch.bfloat16, avail mem=13.58 GB, mem usage=1.22 GB.
[2026-10-12 11:25:04] KV Cache is allocated. #tokens: 57883, K size: 3.09 GB, V size: 3.09 GB
[2026-10-12 11:25:05] INFO:     Uvicorn running on http://127.0.0.1:30001 (Press CTRL+C to quit)
```

ところが、最初の実推論リクエスト(`GET /get_model_info` 後の最初のprefillバッチ)で、
以下のエラーが発生しサーバーがクラッシュした。

```
[2026-10-12 11:25:27] TpModelWorkerClient hit an exception: Traceback (most recent call last):
  ...
  File ".../sgl_kernel/elementwise.py", line 45, in rmsnorm
    torch.ops.sgl_kernel.rmsnorm.default(out, input, weight, eps, enable_pdl)
RuntimeError: RMSNorm failed with error code no kernel image is available for execution on the device
```

`sgl_kernel`(TokenRouterが依存する`sglang`のCUDAカーネル実装パッケージ、v0.3.8)が提供する
`rmsnorm`カーネルの事前コンパイル済みバイナリに、RTX 50シリーズ(Blackwell、sm_120)向けの
カーネルイメージが含まれていない、という意味のエラーである。`torch`自体はpip索引が
`cu128`(CUDA 12.8)ビルドを提供しているためBlackwellを正しく認識できるが、`sgl-kernel`の
バイナリ配布はそれに追いついておらず、GPUという「デバイスの有無」ではなく
**「GPUの世代に対する、依存ライブラリ側のビルド対応状況」**という、別種のハードウェア要件の壁に
あたったことになる。

### 4-3. まとめ

| 項目 | クラウドRoutine環境での結果 | ローカルPCでの結果 |
|---|---|---|
| ライセンス | LICENSEファイル無し、classifierのみ | GitHub自身の自動検出でも未検出(再確認) |
| GPUデバイスの有無 | 存在しない | RTX 5060 Ti(16GB)が存在し、torchも正しく認識 |
| 実際のサーバー起動 | 試行不可 | 起動・モデルロードまでは成功 |
| 実推論 | 試行不可 | `sgl_kernel`がsm_120(Blackwell)向けのビルドを持たず失敗 |

「GPUが無いから動かせない」という当初の制約は、ローカルPCに移しても形を変えて残っていた。
GPU自体はあっても、TokenRouterが依存するCUDAカーネル実装ライブラリの事前ビルド済みバイナリが、
発売されたばかりのハードウェア世代にまだ追いついていなかった、というのが正確な結論である。
本来の検証目的だった「ルーティングあり/なしでのデコードスループット比較」には、今回も到達できなかった。
