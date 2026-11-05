---
title: "NVIDIAの『ループ型』4Bモデル Dory1.0-4B、標準ツールで動かそうとしたら2箇所で止まった"
emoji: "🔁"
type: "tech"
topics: ["ai", "llm", "huggingface", "transformers", "llamacpp"]
published: false
---

## これは何を試した記事か

NVIDIAが公開した[Dory1.0-4B](https://huggingface.co/papers/2611.03998)という4Bパラメータのモデルを、公式のモデルカードが案内するとおりの手順で動かそうとした記事である。
Dory1.0-4Bは、1つの重み(チェックポイント)のまま「再帰ブロックを何回ループさせるか」を1〜4回の間で切り替えることで、再学習なしに推論時の計算量と精度をトレードオフできる「ループ型Transformer」である。
出典は論文(https://huggingface.co/papers/2611.03998 )とモデル重みコレクション(https://huggingface.co/collections/nvidia/nemotron-labs-dory )で、ライセンスはOpenMDW License Agreement version 1.1。
Zenn・Qiita・noteを検索した範囲では、2026年11月4日時点で日本語の一次検証記事は0件だった。

結論を先に書くと、モデルカードのサンプルコードを**そのままコピーして動かす**という最もハードルの低い経路は、2つとも実際に動かなかった。
「GPUが無いから」ではなく、両方とも「モデルの推論エンジン側がまだ`dory`という新しいアーキテクチャに対応していない」というエラーで止まる。
このモデル自体は何も壊れていないので、どこで何のエラーが出たのかを実際のログで残す。

## ライセンス確認

モデルを試す前に、ライセンス全文を取得して確認した。

```
$ curl -sS https://raw.githubusercontent.com/OpenMDW/OpenMDW/refs/heads/main/1.1/LICENSE.OpenMDW-1.1
```

OpenMDW-1.1は、著作権・特許・データベース・トレードシークレット権を含めてモデルを無制限に扱うことを無償で許諾する、実質MIT相当のパーミッシブなライセンスだった。
コピーレフト(派生物も同ライセンスで公開する義務)は無く、再配布時にライセンス全文と著作権表示を残すことだけが条件になっている。
モデルの出力物(生成結果)の利用にも制限を課さないと明記されている。
2026年11月5日時点ではLinux Foundation管理下でOSI承認審議中であり、まだOSI承認済みライセンスにはなっていない。

## アーキテクチャの実際の構成

`config.json`を直接取得して、backlog調査時点の情報(8層の入力ブロック・20層の共有再帰ブロック・8層の出力ブロック)を確認した。

```
$ curl -sS https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16/raw/main/config.json
```

`model_type`は`"dory"`、`architectures`は`["DoryForCausalLM"]`。
`n_input_layers: 16` `n_recurrent_layers: 40` `n_output_layers: 16`(合計72)という値が入っているが、これはAttention/MLPのサブレイヤーをそれぞれ1としてカウントした数で、2で割ると入力8ブロック・再帰20ブロック・出力8ブロックになり、事前に調べていた概要と一致した。
`n_recurrent_loops`はこのBF16版のconfigでは既定2。
sliding_attention層(theta=10000)とfull_attention層(theta=10000000)を交互に使い分けており、256Kコンテキストに対応している。

## 1つ目: `transformers`のサンプルコードをそのまま動かす

モデルカードの`transformers`サンプルは次のように書かれている。

```python
# pip install -U transformers accelerate
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16", device_map="auto"
)
```

`trust_remote_code`やカスタムコードの指定は書かれておらず、「pipでtransformersを更新するだけで動く」という体裁になっている。
2026年11月5日時点のPyPI最新安定版(`transformers` 5.22.1)を実際に入れて試した。

```
$ pip install "transformers>=4.57" accelerate
$ python3 -c "
from transformers import AutoConfig
AutoConfig.from_pretrained('nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16')
"
```

実際に出たエラーはこちらである。

```
ValueError: The checkpoint you are trying to load has model type `dory` but Transformers does not
recognize this architecture. This could be because of an issue with the checkpoint, or because
your version of Transformers is out of date.

You can update Transformers with the command `pip install --upgrade transformers`. If this does
not work, and the checkpoint is very new, then there may not be a release version that supports
this model yet. In this case, you can get the most up-to-date code by installing Transformers
from source with the command `pip install git+https://github.com/huggingface/transformers.git`
```

つまり、モデルカードのサンプルコードが前提にしている`dory`アーキテクチャは、2026年11月5日時点のPyPI安定版にはまだ入っていない。
エラーメッセージ自体がGitHub mainからの再インストールを案内しているが、それが実際に`dory`に対応しているかどうかは、この時点では未確認のままになった(後述)。

## 2つ目: `llama.cpp`(GGUF)をそのまま動かす

モデルカードはGGUF版について「ループ構造に対応したllama.cppのフォーク(PR ggml-org/llama.cpp#30306相当)が必要で、素のllama.cpp/Ollamaは未対応」と明記している。
この主張を、フォークをビルドせずに検証できる方法(PyPIで配布されている`llama-cpp-python`が内部にバンドルしている素のllama.cpp C++コード)で確認した。

```
$ pip install llama-cpp-python
# ビルド成功: llama_cpp_python-0.3.36

$ curl -sS -L -o dory-q5_k_m.gguf \
  "https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-GGUF/resolve/main/NVIDIA-Nemotron-Labs-Dory1.0-4B-Q5_K_M.gguf"

$ sha256sum dory-q5_k_m.gguf
96080be49ffd67b916018b7bdef8c484762576fb52780e10ab98ac4978a660e0
```

このSHA-256はモデルカード記載の値と完全に一致しており、公式配布物そのものをダウンロードできていることを確認した。
これを素の`llama-cpp-python`でロードしようとした。

```
$ python3 -c "
from llama_cpp import Llama
Llama(model_path='dory-q5_k_m.gguf', n_ctx=512, verbose=True)
"
```

GGUFのヘッダ(メタデータ)自体は正しく読み込まれ、`dory.num_loops = 4`や`dory.recurrent_layer_count = 40`といった値もログに表示された。
GGUFのファイル形式としては壊れていないということである。
しかし実際のモデルロードは次のエラーで止まった。

```
print_info: file format = GGUF V3 (latest)
print_info: file type   = Q5_K - Medium
print_info: file size   = 3.41 GiB (7.38 BPW)
llama_model_load: error loading model: unknown model architecture: 'dory'
llama_model_load_from_file_impl: failed to load model
```

モデルカードの記述(素のllama.cpp/Ollamaは未対応)は、実際に手元で動かしても確かにその通りだった。

## ここまでの経路はどちらも、同じ理由で止まっている

`transformers`も`llama.cpp`も、「ファイル自体は正しく読める」「しかし`dory`という新しいアーキテクチャの実装がまだ入っていない」という同じ理由で止まった。
GPUが無いから遅い、メモリが足りない、といった計算資源の問題ではなく、推論エコシステム側の対応がまだ追いついていないという話である。
論文公開直後のモデルではよくあることだが、「モデルカードに書かれた手順をそのままコピーすれば動く」と思って試すと、現時点ではここで止まる。

モデルカードはこの先の回避策として、(1)`transformers`をGitHub本家リポジトリのmain branchから入れ直す、(2)専用フォークのllama.cpp(`brianchmielNV/llama.cpp`、特定コミットにpin)をビルドする、という2つの道を示している。
筆者の作業環境(Claude Code Routineのクラウド実行環境)では、外部ソースから取得した未レビューのコードをビルド・インストールする操作自体がセキュリティポリシーでブロックされており、この2つの回避策を実際に試すことができなかった。
ここは「動かした結果」ではなく「まだ試せていない」として正直に書く。
ローカルPCでの再現手順は本検証のリポジトリに記録してあり、結果が出たら追記する。

## まとめ

- OpenMDW-1.1ライセンスは実質MIT相当で、商用利用を含め問題なく使える。
- `config.json`から、backlog調査時点の「8層入力+20層再帰+8層出力」という構成を実機で確認した。
- モデルカードの`transformers`サンプルコードは、2026年11月5日時点のPyPI安定版(5.22.1)では`dory`アーキテクチャ未対応のため実際に動かなかった。
- モデルカードのGGUF版も、SHA-256まで一致する公式配布ファイルを使っても、素の`llama-cpp-python`では`unknown model architecture: 'dory'`で実際に動かなかった。
- どちらも「公式サンプルコードのコピペ」という最も低いハードルの経路で確実に再現できる、現時点でのエコシステム対応状況の記録である。
- ループ回数1と4のBefore/After比較そのものは、推奨される回避策(GitHub mainのtransformers、または専用フォークのllama.cpp)を使わないと到達できず、今回は確認できなかった。
