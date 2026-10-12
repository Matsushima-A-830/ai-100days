---
title: "ライセンス不明のOSSは記事にできなかったが、GPU側の「動かない」はsglangへの小さなパッチで越えられた"
emoji: "🔧"
type: "tech"
topics: ["ai", "llm", "oss", "cuda", "python"]
published: false
---

筆者は海外のAI関連ニュースを毎日1本検証して発信するチャレンジの14日目として、Hugging Face Daily Papersに掲載されていた[TokenRouter](https://github.com/thu-nics/TokenRouter)(thu-nics)を検証しようとした。複数のLLMをトークン単位で動的に振り分け、大きなモデルと小さなモデルを組み合わせて推論コストを抑える、というルーティング手法の実装である。

結論から書く。**TokenRouter自体のライセンスが未確定だったため、このツールのコードや検証結果を記事の主役にすることはできなかった。** 一方で、検証の途中で踏んだ「最新世代のGPUでは動かない」という別の壁は、最終的に自分の手でsglang(TokenRouterが依存する推論サーバー)のソースにパッチを当てることで、実際に越えることができた。今回はその過程を書く。

## 1つ目の壁: ライセンスが未確定

検証に着手する前に、CLAUDE.mdの「ライセンスを確認する」というルールに従ってリポジトリを確認した。

```
$ find /tmp/tokenrouter-license-check -iname "*licen*" -o -iname "*copying*" -o -iname "*notice*"
(該当ファイルなし)
```

リポジトリルートにLICENSE・COPYING・NOTICEのいずれも存在しない。`pyproject.toml`の`classifiers`に`"License :: OSI Approved :: Apache Software License"`という分類タグがあるだけで、ライセンス全文もREADME上の言及も無かった。GitHub自身のライセンス自動検出(`gh api repos/thu-nics/TokenRouter`の`license`フィールド)でも`null`、つまり未検出という結果を別経路で確認した。

このため、TokenRouter自体のコードを転載したり、その検証結果を記事の主役にすることは避けた。この記事で書くのは、TokenRouterというきっかけから見えてきた、もう一段下の層(GPUの世代とCUDAライブラリの対応状況)の話である。

## 2つ目の壁: クラウドの検証環境にGPUが無い

このチャレンジは通常、クラウド上の自動実行環境(Routine)が検証コードを書いて実行する。しかしTokenRouterの公式サンプル構成は、大きいモデル(Qwen3-32B、`tp_size: 2`で複数GPU前提)と小さいモデル(Qwen3-0.6B)をCUDA MPSで同一GPU上に共存させる構成しか用意されておらず、依存ライブラリ(`sglang`・`sgl-kernel`・`flashinfer-python`等)もすべてNVIDIA CUDA専用だった。

```
$ nvidia-smi
bash: nvidia-smi: command not found
$ python3 -c "import torch; print(torch.cuda.is_available())"
ModuleNotFoundError: No module named 'torch'
```

Routineのクラウド実行環境にはGPUデバイス自体が存在しない。インストールも実行も試せないまま、ここでローカル検証にエスカレーションした。

## ローカルで判明した3つ目の壁: GPU世代が新しすぎる

自分のPC(RTX 5060 Ti、16GB、Blackwell世代/Compute Capability sm_120)で、実際に環境を構築した。

```bash
pip install -e .   # torch==2.8.0, sglang==0.5.1, sgl-kernel==0.3.8 等、全て成功
```

依存関係のインストールは成功し、torchもGPUを正しく認識した。公式configが要求するQwen3-32B(複数GPU)はGPU1枚・16GBのこの環境では不可能なため、代わりに軽量なQwen3-0.6B単体で`sglang.launch_server`を起動したところ、サーバー起動・モデルのGPUロードまでは成功した。

ところが、最初の実推論リクエストで次のエラーが発生し、サーバーがクラッシュした。

```
RuntimeError: RMSNorm failed with error code no kernel image is available for execution on the device
```

`sgl_kernel`(sglangが使うCUDAカーネルの実装パッケージ、当時のバージョンは0.3.8)が同梱する事前コンパイル済みバイナリに、RTX 50シリーズ(Blackwell、sm_120)向けのカーネルイメージが含まれていなかった。torch自体はcu128ビルドでBlackwellに対応していたが、`sgl-kernel`のバイナリ配布がそこに追いついていない。「GPUがあるかどうか」ではなく「GPU世代に対して依存ライブラリのビルドが追いついているかどうか」という、別種の壁だった。

## 回避策1: sgl-kernelを新しいバージョンに差し替える

`sgl-kernel`の新しいバージョンならBlackwellに対応しているのでは、という仮説を実際に試した。`torch==2.8.0`は変えずに、`sgl-kernel`だけを段階的に新しいバージョンへ差し替え、importできるか(torchとのC++ ABI互換性があるか)を二分探索した。

| sgl-kernelバージョン | torch==2.8.0とのimport |
|---|---|
| 0.3.8(元の指定) | OK(ただしRMSNormでsm_120未対応エラー) |
| 0.3.9 / 0.3.12 / 0.3.14 / 0.3.16 / 0.3.18 | OK |
| 0.3.21(最新) | NG(`undefined symbol: _ZNK3c106SymInt...`) |

最新の0.3.21は、こちらのtorchより新しいバージョン向けにビルドされているらしく、C++シンボルの不一致でimportすら失敗した。0.3.9から0.3.18まではimport自体に問題は無かった。

importできた最新版の0.3.18で、問題のRMSNormカーネルだけを直接呼び出して確認したところ、実際にBlackwell上で正常に動作した。

```python
from sgl_kernel import rmsnorm
out = rmsnorm(x, w, 1e-6)  # RTX 5060 Ti上で正常終了
```

`sgl_kernel`パッケージの中にアーキテクチャ別バイナリ(`sm90`・`sm100`)のディレクトリが新設されており、sm_120のGPUには`sm100`向けバイナリが使われる仕組みになっていた。0.3.8の時点ではこの分割自体が無く、Blackwellのカーネルイメージが欠けていたのだと分かった。

## 回避策1の壁: sglang本体が新しいAPIに追従していない

ここで満足せず、`sgl-kernel==0.3.18`に差し替えた状態で`sglang==0.5.1`(TokenRouter指定バージョン)のサーバーを実際に起動してみた。すると、RMSNormとは別の場所で止まった。

```
ImportError: cannot import name 'fused_marlin_moe' from 'sgl_kernel'
```

`sgl-kernel`側でMoE/Marlin量子化関連の関数群が再構成され、`fused_marlin_moe`という名前の関数が無くなっていた(`moe_wna16_marlin_gemm`などに置き換わっていた)。`sglang==0.5.1`はこの関数を量子化を使う/使わないに関わらず起動時に無条件でimportするため、サーバー自体が起動できなかった。

## 回避策2: 使われない機能のimportだけを遅延させる

ここでソースを読みに行った。`fused_marlin_moe`が実際に**呼び出されている**場所は、`sglang`のソース全体で2箇所(`awq.py`と`gptq.py`、それぞれAWQ/GPTQ版のMoE量子化メソッド内)だけだった。手元で動かしているQwen3-0.6Bはbf16(量子化なし)なので、どちらも実行時には一度も呼ばれない。問題は「importされているかどうか」だけで、「呼び出されるかどうか」ではなかった。

ローカルの`.venv`にインストール済みの`sglang`パッケージのこの2ファイルだけ、importを`try/except`で囲む最小限のパッチを当てた(TokenRouterのリポジトリや`sgl-kernel`本体には変更を加えていない)。

```python
if _is_cuda:
    from sgl_kernel import awq_dequantize, awq_marlin_moe_repack, awq_marlin_repack
    try:
        from sgl_kernel import fused_marlin_moe
    except ImportError:
        fused_marlin_moe = None  # AWQ-MoE量子化モデルを使う場合のみ必要
```

この状態でサーバーを再起動すると、以前クラッシュしていた最初の推論リクエストを正常に通過した。

```bash
curl http://127.0.0.1:30003/generate -d '{"text": "The capital of France is", "sampling_params": {"max_new_tokens": 16, "temperature": 0}}'
```

```json
{"text":" Paris. The capital of France is also the capital of the Republic of France.", ...}
```

エラーなく、最後まで生成が完了した。0.6Bモデル・greedy decodingゆえに文章自体はやや繰り返し気味だが、Blackwell上でTokenRouterが依存する推論スタックが最後まで動いたという事実が重要だった。

## まとめ

今回はTokenRouter自体のライセンスが未確定だったため、その検証結果を記事の主役にすることはできなかった。しかし検証の途中で踏んだ「最新世代のGPUでは依存ライブラリが追いついていない」という壁は、(1)依存パッケージを新しいバージョンに差し替え、(2)それでも残る小さなAPIの食い違いをソースを読んでパッチする、という2段階の作業で、実際に越えられることを確認した。

エラーメッセージを見て「動かない」で終わらせず、依存関係の中のどのバージョンのどの関数が問題なのかを実際に切り分けていくと、意外と小さな変更で解決できることがある。発売されたばかりのGPU世代を使っていると、こうした「ライブラリのビルドがまだ追いついていない」という壁に今後も何度か当たりそうだが、今回のように手順を分解して確認していけば、越えられる場合もあると分かったのは良い収穫だった。

- 出典(ライセンス未確定につき転載は行っていない): https://github.com/thu-nics/TokenRouter
- パッチ対象: `sglang==0.5.1`(Apache-2.0、https://github.com/sgl-project/sglang )
- 検証環境: NVIDIA GeForce RTX 5060 Ti(16GB、Blackwell/sm_120)、`torch==2.8.0+cu128`
