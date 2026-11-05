# Day 038 検証結果 — NVIDIA Nemotron Labs/Dory1.0-4B

対象: https://huggingface.co/papers/2611.03998 (論文)
モデル重みコレクション: https://huggingface.co/collections/nvidia/nemotron-labs-dory
ライセンス: OpenMDW License Agreement, version 1.1

検証日時: 2026-11-05 (UTC)
検証環境: Claude Code Routine クラウド実行環境(GPU無し、CPU 4コア、RAM 15GB、ディスク空き約30GB)

## 1. ライセンス確認(OpenMDW-1.1)

ライセンス全文を取得して確認した。

```
$ curl -sS https://raw.githubusercontent.com/OpenMDW/OpenMDW/refs/heads/main/1.1/LICENSE.OpenMDW-1.1
```

要点:

- 「Model Materials」(モデル・パラメータ・関連ドキュメント/ソフトウェア)について、著作権・特許・データベース・トレードシークレット権を含め**無制限に扱うことを無償で許諾**する、MITに近い非常にパーミッシブなライセンス。コピーレフト(派生物も同ライセンスで公開する義務)は無い。
- 再配布時はライセンス全文と著作権表示の保持のみが条件。
- モデルの出力物(生成結果)の利用・改変・共有には一切制限を課さないと明記。
- 特許・著作権訴訟を起こした場合に権利が終了するパテントリタリエーション条項あり(Apache-2.0と似た構造)。
- 無保証・免責条項(MIT/Apacheと同様の標準的な文言)。
- 2026-11-05時点でLinux Foundation管理下でOSI承認審議中(backlog.md記載の通り、本検証時点ではまだOSI承認済みライセンスではない)。

結論: 商用・非商用問わず利用可能な、実質MIT相当のパーミッシブなライセンス。追加の有料APIキーは不要。

## 2. アーキテクチャ確認(config.json実測)

```
$ curl -sS https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16/raw/main/config.json
```

実際の値:

- `architectures`: `["DoryForCausalLM"]` / `model_type`: `"dory"`
- `n_input_layers`: 16, `n_recurrent_layers`: 40, `n_output_layers`: 16 (`num_hidden_layers`: 72)
  - これはattention/MLPのサブレイヤーをそれぞれ1層として数えた値で、2で割ると入力8ブロック・再帰20ブロック・出力8ブロックとなり、backlog.mdの記述(8/20/8)と一致することを確認した。
- `n_recurrent_loops`: 2 (BF16版のconfig.json上のデフォルト値)
- `hidden_size`: 2560, `vocab_size`: 131072, `max_position_embeddings`: 262144(256Kコンテキストに対応)
- rope_parametersでsliding_attention層(theta=10000)とfull_attention層(theta=10000000)の2種類を使い分けていることを確認。

## 3. 推論方法の実動作確認

モデルカードが案内する3つの推論経路(transformers / llama.cpp / vLLM)のうち、**追加の有料APIキーなしでCPUだけで試せる2つ(transformers, llama.cpp)を実際に試した。**

### 3-1. `transformers`経由(pip公開の安定版) — 実際に動かして失敗を確認

モデルカードのサンプルコードは`pip install -U transformers accelerate`後に`AutoModelForCausalLM.from_pretrained(...)`するだけで、`trust_remote_code`やカスタムコードの指定は書かれていない。まず安定版で試した。

```
$ pip3 install "transformers>=4.57" accelerate
(インストール済み: transformers 5.22.1 / torch 2.15.0 / 2026-11-05時点でのPyPI最新安定版)

$ python3.13 -c "
from transformers import AutoConfig
cfg = AutoConfig.from_pretrained('nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16')
"
```

実際の出力(そのまま):

```
ValueError: The checkpoint you are trying to load has model type `dory` but Transformers does not
recognize this architecture. This could be because of an issue with the checkpoint, or because
your version of Transformers is out of date.

You can update Transformers with the command `pip install --upgrade transformers`. If this does
not work, and the checkpoint is very new, then there may not be a release version that supports
this model yet. In this case, you can get the most up-to-date code by installing Transformers
from source with the command `pip install git+https://github.com/huggingface/transformers.git`
```

**結論: 2026-11-05時点でPyPIの最新安定版`transformers` 5.22.1には`dory`アーキテクチャがまだ組み込まれておらず、モデルカードのサンプルコードをそのままコピーしても動かない。** エラーメッセージ自体が案内する「GitHub mainからのインストール」が必要かどうかは本Routine環境では検証できなかった(詳細は4節)。

### 3-2. `llama.cpp`経由(PyPI公開の`llama-cpp-python`、素のllama.cppをバンドル) — 実際に動かして失敗を確認

モデルカードは「素のllama.cpp/Ollamaではなく、ループ構造対応のフォーク(PR ggml-org/llama.cpp#30306)が必要」と明記している。この主張自体を、フォークをビルドせずに検証可能な方法(PyPI公開の`llama-cpp-python`が内部にバンドルしている素のllama.cpp C++コードでGGUFをロードする)で実際に確認した。

```
$ pip3 install llama-cpp-python
(ビルド成功: llama_cpp_python-0.3.36、所要時間 約3分8秒)

$ curl -sS -L -o dory-q5_k_m.gguf \
  "https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-GGUF/resolve/main/NVIDIA-Nemotron-Labs-Dory1.0-4B-Q5_K_M.gguf"
(ダウンロード成功: 3,673,288,864 bytes、所要時間 約2分8秒)

$ sha256sum dory-q5_k_m.gguf
96080be49ffd67b916018b7bdef8c484762576fb52780e10ab98ac4978a660e0
```

→ モデルカード記載のSHA-256 (`96080be49ffd67b916018b7bdef8c484762576fb52780e10ab98ac4978a660e0`) と完全一致。ダウンロードしたファイルは公式配布物そのものであることを確認した。

```
$ python3.13 -c "
from llama_cpp import Llama
llm = Llama(model_path='dory-q5_k_m.gguf', n_ctx=512, verbose=True)
"
```

実際の出力(ログから抜粋、そのまま):

```
llama_model_loader: - kv  19:                     dory.input_layer_count u32              = 16
llama_model_loader: - kv  20:                 dory.recurrent_layer_count u32              = 40
llama_model_loader: - kv  21:                    dory.output_layer_count u32              = 16
llama_model_loader: - kv  22:                             dory.num_loops u32              = 4
print_info: file format = GGUF V3 (latest)
print_info: file type   = Q5_K - Medium
print_info: file size   = 3.41 GiB (7.38 BPW)
llama_model_load: error loading model: unknown model architecture: 'dory'
llama_model_load_from_file_impl: failed to load model
ValueError: Failed to load model from file: dory-q5_k_m.gguf
```

**結論: PyPIで配布されている標準的な`llama-cpp-python`(=素のllama.cpp)は、GGUFのヘッダ(メタデータ)自体は正しく読めるが、`dory`アーキテクチャの実装が無いため「unknown model architecture: 'dory'」で確実に失敗する。** これはモデルカード自身の記述(素のllama.cpp/Ollamaでは動かない)と一致する、再現可能な実際の失敗である。GGUFメタデータから`dory.num_loops=4`がこのQ5_K_M量化ファイルの既定値として埋め込まれていることも確認した(モデルカードによれば`--override-kv`で1〜4に変更可能、本Routine環境ではロード自体が失敗するため実際の切り替え比較は未実施)。

## 4. ローカル検証待ちの項目(Routine環境の制約)

以下2点は、**本Claude Code Routineのクラウド実行環境が持つ「外部ソースから取得した未レビューのコードのビルド・インストールをブロックする」という自動判定ポリシーにより、本Routine内では試行できなかった。** これは通常のPC環境であれば発生しない、本実行環境固有の制約であり、Dory1.0-4Bというツール自体の挙動を示すものではないため、記事では「失敗」として書かず、ローカル検証にエスカレーションする。

- **(a) `pip install git+https://github.com/huggingface/transformers.git`** (transformers公式リポジトリのmain branchを使った`dory`アーキテクチャ対応の有無の確認)
- **(b) モデルカード記載のフォーク版llama.cppのビルド**(`https://github.com/brianchmielNV/llama.cpp.git`、pin commit `98a74c97ea09ac72f6ceda1559808fc0a2f447ce`)とそれを使ったループ回数1/4でのBefore/After比較

どちらも試行しようとした時点で「Permission for this action was denied by the Claude Code auto mode classifier. Reason: [Code from External]」という同種の拒否が発生し、それ以上の情報(実際にビルドが成功するか、実際にエラーが出るか)は本Routine環境では得られなかった。したがって「動かなかった」とは書かず、**Routine環境の制約により未検証、ローカル検証待ち**とする。再現手順は`README.md`に記載。

## 5. 参考: NVIDIA自己報告のベンチマーク数値(論文より、第三者再現は未確認)

論文(arXiv:2611.03998)記載の数値をそのまま引用する(本Routineでの実測値ではない)。

- 12ベンチマーク平均: 1ループ 35.17 / 2ループ 39.67 / 4ループ 40.60(比較: Qwen3.5-9B 32.21, Gemma 4 12B 32.59, Gemma 4 26B-A4B 36.73, Qwen3.6-35B-A3B 42.30)
- SWE-bench Verified: 1ループ 50.3 / 2ループ 59.5 / 4ループ 61.8
- 出力トークン数(Table 3、1回の試行あたり): GDPval-AA v2 212k→85k(約2.5倍減)、Terminal-Bench v2.1 109k→54k(約2.0倍減)、SWE-bench Verified 33.6k→24.8k(約1.35倍減)、τ³-Banking 23.0k→17.6k(約1.3倍減)

## 6. ローカル検証(人間のGPU環境、2026-11-05)

検証環境: NVIDIA GeForce RTX 5060 Ti(16GB VRAM、Blackwell)、CUDA 12.8、torch 2.11.0+cu128。

### 6-1. `transformers`をGitHub mainから入れ直す(モデルカード/エラーメッセージが案内する回避策(a))

```
$ pip install -U "git+https://github.com/huggingface/transformers.git"
(インストール成功: transformers 5.23.0.dev0)

$ python3 -c "
from transformers import AutoConfig
AutoConfig.from_pretrained('nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16')
"
```

実際の出力(そのまま):

```
KeyError: 'dory'
...
ValueError: The checkpoint you are trying to load has model type `dory` but Transformers does not
recognize this architecture. ...
```

**結論: GitHub mainからビルドした`transformers`(5.23.0.dev0、2026-11-05時点のmain)でも、`dory`アーキテクチャはまだ実装されていない。** エラーメッセージが案内する回避策どおりにしても解決しなかった、という回避策自体の不備である。これは本Routine環境の制約ではなく、手元のGPU環境で実際にmainブランチをビルドしてもなお再現する失敗であり、検証に直接関係する失敗として扱う。

### 6-2. モデルカード記載のフォーク版llama.cppをビルドしてループ回数1/4のBefore/After比較(回避策(b))

```
$ REV=98a74c97ea09ac72f6ceda1559808fc0a2f447ce
$ git clone https://github.com/brianchmielNV/llama.cpp.git llama.cpp-dory
$ git -C llama.cpp-dory checkout --detach "$REV"
$ cmake -S llama.cpp-dory -B llama.cpp-dory/build \
    -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=ON -DGGML_CUDA_GRAPHS=ON -DCMAKE_CUDA_ARCHITECTURES=120
$ cmake --build llama.cpp-dory/build --target llama-server --parallel
(ビルド成功)
```

**結論: 専用フォーク版llama.cppはビルドに成功し、素のllama.cppでは`unknown model architecture: 'dory'`で失敗していたのと対照的に、同じGGUFファイル(SHA-256: `96080be4...a660e0`、モデルカード値と一致)を問題なくロードできた。** モデルカードの主張(専用フォークが必要)はこれで裏付けられた。

続けてループ回数1と4でサーバーを別々に起動し、同一プロンプト(「電車が120kmを2時間、続けて180kmを3時間走った。全体の平均速度は?」の英語版、`--override-kv dory.num_loops=int:1|4,dory.recurrent_kv_cache_mode=str:per_loop`、`temperature=0`、`max_tokens=3000`)を投げて比較した。

| | num_loops=1 | num_loops=4 |
|---|---|---|
| 応答 | 正解(60 km/h、結論のみ約1130トークン) | 正解(60 km/h、結論のみ約1157トークン) |
| completion_tokens | 1130 | 1157 |
| 所要時間(壁時計) | 39.97秒 | 129.23秒 |
| トークン/秒 | 約28.3 tok/s | 約8.96 tok/s |

実際の出力(抜粋、そのまま):

```
# num_loops=1
**Step 1: Find the total distance traveled**
...
Average speed = Total distance ÷ Total time
Average speed = 300 km ÷ 5 hours = 60 km/h

# num_loops=4
To find the average speed for the entire trip, use the formula:
Average Speed = Total Distance / Total Time
...
Therefore, the train's average speed for the whole trip is 60 km/h.
```

**結論: 今回のような単純な算数問題では、ループ回数を1→4に増やしても出力トークン数は減らず(1130→1157でわずかに増加)、生成時間だけが約3.2倍に伸びた(39.97秒→129.23秒)。** 両方とも正解(60 km/h)には到達している。論文(5節参照)が報告する「出力トークン数の削減」はGDPval-AAやSWE-bench VerifiedのようなLLM自身が長い思考過程を必要とする難しいタスクでの効果であり、今回使った単純な算数問題のように元々の思考過程が短いタスクでは、ループを増やす効果(少ない出力で同じ精度に到達する)は現れず、むしろループ回数分だけ1トークンあたりの計算量が増えて生成が遅くなる、という素直な結果になった。

## まとめ

- ライセンス(OpenMDW-1.1)は実質MIT相当で商用利用も含め問題なし。
- モデルカードのサンプルコードをそのままコピーしても、2026-11-05時点のPyPI安定版`transformers`では`dory`アーキテクチャ未対応で**実際に失敗する**(確認済み)。
- 標準的な(PyPI配布の)`llama-cpp-python`=素のllama.cppでも、GGUFのロード自体が`unknown model architecture: 'dory'`で**実際に失敗する**(確認済み、SHA-256でファイル同一性も確認済み)。
- ローカルのGPU環境で確認したところ、**GitHub mainから入れ直した`transformers`(5.23.0.dev0)でも`dory`アーキテクチャは未実装のままで、エラーメッセージが案内する回避策自体が機能しなかった。**
- 一方、モデルカード記載の専用フォーク版llama.cpp(`brianchmielNV/llama.cpp`、pin commit)はビルド・ロードに成功し、ループ回数1と4のBefore/After比較まで実施できた。同じ平均速度算出問題では、ループ回数を増やしても出力トークン数は減らず、生成時間が約3.2倍に伸びるだけだった(単純なタスクでは論文が主張する「出力トークン削減」効果は現れない)。
