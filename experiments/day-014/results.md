# Day 014 — TokenRouter(thu-nics) 検証結果

**結論: Routine実行環境の制約(CUDA GPUが存在しない)およびライセンス表記の不備により、
実際のルーティング/スループット検証には進めなかった。人間がローカルPC(RTX 5060 Ti, 16GB)で
検証した結果、ライセンス不備は再確認、GPU面では新たに「ハードウェア世代の非対応」という
別種のブロッカーが判明した。このGPUブロッカーは、`sgl-kernel`を新しいバージョン(0.3.18)に
差し替え、`sglang`側の2ファイルに小さなソースパッチ(使われないimportの遅延)を当てることで、
**最終的にBlackwell上での実推論まで動作させることができた。** ライセンス不備は未解消のまま
(詳細は末尾の追記セクション、特に「6. 追記」)。**

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

## 5. 追記(2026-10-12、回避策の検証: sgl-kernelの新しいバージョンを試す)

`sgl-kernel`の新しいバージョンがBlackwell(sm_120)に対応していないか、実際に試した。

```
$ pip index versions sgl-kernel
sgl-kernel (0.3.21)
Available versions: 0.3.21, 0.3.20, ..., 0.3.9, 0.3.8, ...
```

TokenRouterが指定する`torch==2.8.0`を変えずに、`sgl-kernel`だけを`--no-deps`で
段階的に新しいバージョンへ差し替え、importできるか(torchとのC++ ABI互換性があるか)を
二分探索的に確認した。

| sgl-kernelバージョン | torch==2.8.0とのimport | 備考 |
|---|---|---|
| 0.3.8(元の指定) | OK | RMSNormでsm_120未対応エラー(上記4-2) |
| 0.3.9 / 0.3.12 / 0.3.14 / 0.3.16 / 0.3.18 | **OK** | いずれもエラーなくimportできた |
| 0.3.21(最新) | **NG** | `undefined symbol: _ZNK3c106SymInt22maybe_as_int_slow_pathEv`(torchのC++ ABI不一致) |

0.3.21は読み込み時点で、torch側のC++クラス(`c10::SymInt`)のシンボルが見つからずimportに失敗した。
これは`sgl-kernel`の0.3.21が、こちらの`torch==2.8.0`とは異なる(より新しい)torchバージョン向けに
ビルドされているためと考えられる。一方、0.3.9〜0.3.18の間はimport自体は成功した。

### RMSNormカーネル単体では、実際にBlackwellで動いた

importできた最新版の`0.3.18`で、問題のRMSNormカーネルだけを直接呼び出して確認した。

```python
import torch
from sgl_kernel import rmsnorm
x = torch.randn(4, 128, device='cuda', dtype=torch.bfloat16)
w = torch.ones(128, device='cuda', dtype=torch.bfloat16)
out = rmsnorm(x, w, 1e-6)
torch.cuda.synchronize()
print('RMSNORM_KERNEL_OK', out.shape, out.dtype)
```

```
RMSNORM_KERNEL_OK torch.Size([4, 128]) torch.bfloat16
```

`sgl_kernel`パッケージ内に`sm90`/`sm100`というアーキテクチャ別バイナリのディレクトリがあり、
sm_120(Blackwell)のGPUには`sm100`向けバイナリが使われる仕組みになっていた。
0.3.8の時点ではこの仕組み自体が無く(アーキテクチャ別バイナリの分割がない単一バイナリ)、
sm_120向けのカーネルイメージが欠けていた。0.3.9〜0.3.18のどこかでこの分割が入り、
Blackwellのカーネルイメージが追加されたと考えられる。
**→ RMSNorm単体では、0.3.8→0.3.18への差し替えでBlackwell非対応問題が解消することを実機で確認できた。**

### ただしsglang==0.5.1本体の起動では別のAPI不整合で失敗した

`sgl-kernel==0.3.18`に差し替えた状態で、TokenRouterが指定する`sglang==0.5.1`の
`sglang.launch_server`を実際に起動しようとしたところ、RMSNormとは別の箇所でエラーになった。

```
File ".../sglang/srt/layers/quantization/awq.py", line 44, in <module>
    from sgl_kernel import (
ImportError: cannot import name 'fused_marlin_moe' from 'sgl_kernel'
```

`sgl-kernel`側でMoE/Marlin量子化関連の関数群が0.3.8から0.3.18までの間に再構成されており
(`fused_marlin_moe`という名前の関数がもう存在せず、`moe_wna16_marlin_gemm`など別名の
関数群に置き換わっていた)、`sglang==0.5.1`はこのモジュールを(量子化を使う/使わないに関わらず)
起動時に無条件でimportするため、サーバー自体が起動できなかった。

Qwen3-0.6Bはbf16(量子化なし)で動かすため、この量子化コード自体は本来不要だが、
import自体が無条件に実行される設計のため回避できなかった。

**→ まとめ(このセクション時点): `sgl-kernel`を新しいバージョンに差し替えるだけでは、TokenRouterが指定する
`sglang==0.5.1`との組み合わせでは動かせなかった。RMSNormカーネル自体はBlackwellで
動作することを実機で確認できたが、`sglang`側のPython APIが`sgl-kernel`の新しいバージョンの
API変更に追従していないため、`sglang`自体のアップグレード、または`sglang`のソース側を
パッチする(量子化モジュールのimportを回避する等)作業が追加で必要になる。**
(この後、実際にソースパッチまで踏み込んで最終的に動作させた。「6. 追記」を参照。)

## 6. 追記(2026-10-12、ソースパッチによる最終的な動作確認)

「`sglang`のソース側をパッチする」という回避策を、実際に手を動かして試した。

### 原因の特定: `fused_marlin_moe`は2箇所でのみimportされ、どちらも呼び出されるのは量子化モデルのみ

```
$ grep -rn 'fused_marlin_moe' .venv/lib/python3.12/site-packages/sglang/
.../layers/quantization/awq.py:48:        fused_marlin_moe,
.../layers/quantization/awq.py:756:        return fused_marlin_moe(
.../layers/quantization/gptq.py:55:    from sgl_kernel import fused_marlin_moe, ...
.../layers/quantization/gptq.py:1074:        return fused_marlin_moe(
```

`fused_marlin_moe`は`sgl_kernel==0.3.18`には存在しないが(関数群が`moe_wna16_marlin_gemm`などに
再構成されたため)、実際に**呼び出されている**のは`awq.py`と`gptq.py`それぞれのAWQ/GPTQ版MoE量子化
メソッド内の1箇所だけだった。Qwen3-0.6Bはbf16(量子化なし)で動かすため、この呼び出し自体は
実行時には一度も使われない。問題は「importされているかどうか」だけであり、「呼び出せるかどうか」
ではなかった。

### パッチ内容: importをtry/exceptで囲んで未使用時は`None`にする

`awq.py`(44行目付近)と`gptq.py`(55行目付近)の、CUDA時に`fused_marlin_moe`をimportしている
箇所を、以下のように変更した(ローカルの`.venv`内のインストール済みファイルを直接編集。
リポジトリや`sgl-kernel`本体には一切変更を加えていない)。

```python
# awq.py
if _is_cuda:
    from sgl_kernel import (
        awq_dequantize,
        awq_marlin_moe_repack,
        awq_marlin_repack,
    )
    try:
        from sgl_kernel import fused_marlin_moe
    except ImportError:
        fused_marlin_moe = None  # AWQ-MoE量子化モデルを使う場合のみ必要

# gptq.py
if _is_cuda:
    from sgl_kernel import gptq_gemm, gptq_marlin_repack, gptq_shuffle
    try:
        from sgl_kernel import fused_marlin_moe
    except ImportError:
        fused_marlin_moe = None  # GPTQ-MoE量子化モデルを使う場合のみ必要
```

### 結果: サーバー起動・実推論まで到達した

```bash
python3 -m sglang.launch_server --model-path Qwen/Qwen3-0.6B --port 30003 \
  --mem-fraction-static 0.5 --disable-cuda-graph
```

```
[2026-10-12 11:57:12] Load weight end. type=Qwen3ForCausalLM, dtype=torch.bfloat16, avail mem=13.58 GB, mem usage=1.22 GB.
[2026-10-12 11:57:12] KV Cache is allocated. #tokens: 57883, K size: 3.09 GB, V size: 3.09 GB
[2026-10-12 11:57:14] INFO:     Uvicorn running on http://127.0.0.1:30003 (Press CTRL+C to quit)
[2026-10-12 11:57:15] Prefill batch. #new-seq: 1, #new-token: 6, #cached-token: 0, token usage: 0.00, #running-req: 0, #queue-req: 0,
```

以前はこの直後(最初のprefillバッチ)で`RuntimeError: RMSNorm failed...`が発生してクラッシュしていたが、
今回はクラッシュせずサーバーが起動し続けた。実際にcurlで推論リクエストを送って確認した。

```bash
curl -s http://127.0.0.1:30003/generate -H 'Content-Type: application/json' \
  -d '{"text": "The capital of France is", "sampling_params": {"max_new_tokens": 16, "temperature": 0}}'
```

```json
{"text":" Paris. The capital of France is also the capital of the Republic of France.","output_ids":[785,6722,315,9625,374,12095,13,576,6722,315,9625,374,1083,279,6722,315,279,5429,315,9625,13],"meta_info":{"id":"4df83b83808645d29d7ed1af87e3fd05","finish_reason":{"type":"length","length":16},"prompt_tokens":5,"weight_version":"default","completion_tokens":16,"cached_tokens":2,"e2e_latency":11.269001960754395}}
```

**実際にBlackwell(RTX 5060 Ti)上で、TokenRouterが依存する`sglang`サーバー経由の推論が
最後まで動作することを確認できた。** 出力文自体は0.6Bモデル・greedy decodingゆえの
繰り返し気味な内容だが、エラーなく最後まで生成が完了している点が重要な結果である。

### この結果の位置づけ

- 変更したのは**ローカルの`.venv`にインストールされた`sglang`パッケージの2ファイル**のみ。
  TokenRouterのリポジトリ自体や`sgl-kernel`本体には変更を加えていない。
- パッチの内容は「使われない機能(AWQ/GPTQのMoE量子化)のimportを遅延させる」という
  最小限のものであり、Qwen3-0.6B(bf16・量子化なし)の動作には影響しない。
- 公式のTokenRouter configが前提とする構成(Qwen3-32B + Qwen3-0.6B、複数GPU)での
  本来のルーティング検証には、このGPU1枚・16GBの環境では別途モデルサイズの制約が残る。
  今回確認できたのは「軽量モデル単体なら、Blackwell上でもsglangサーバーとして動く」という、
  GPU世代の壁そのものを越えられることの実証である。

**→ まとめ(最終): 「GPUの世代が新しすぎて対応していない」というブロッカーは、
(1) `sgl-kernel`を0.3.8→0.3.18に差し替え、(2) `sglang`側の2ファイルに
使われない機能のimportを遅延させる小さなパッチを当てる、という2段階の作業で
実際に解消できた。ライセンス不備というもう一つのブロッカーは今回の作業では解消していない。**
