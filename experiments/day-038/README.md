# Day 038 — NVIDIA Nemotron Labs/Dory1.0-4B

## 対象

- 論文: https://huggingface.co/papers/2611.03998 (Dory1.0-4B: A Looped Normalized-GPT)
- モデル重みコレクション: https://huggingface.co/collections/nvidia/nemotron-labs-dory
- ライセンス: OpenMDW License Agreement, version 1.1 (https://raw.githubusercontent.com/OpenMDW/OpenMDW/refs/heads/main/1.1/LICENSE.OpenMDW-1.1)

## このRoutineで実際に行ったこと(再現手順)

### 1. ライセンス確認

```bash
curl -sS https://raw.githubusercontent.com/OpenMDW/OpenMDW/refs/heads/main/1.1/LICENSE.OpenMDW-1.1
```

### 2. config.jsonでアーキテクチャ確認

```bash
curl -sS https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16/raw/main/config.json
```

### 3. `transformers`(PyPI安定版)での動作確認(失敗することを確認)

```bash
pip install "transformers>=4.57" accelerate
python3 -c "
from transformers import AutoConfig
AutoConfig.from_pretrained('nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16')
"
# => ValueError: ... model type `dory` ... Transformers does not recognize this architecture ...
```

### 4. `llama-cpp-python`(PyPI、素のllama.cppをバンドル)での動作確認(失敗することを確認)

```bash
pip install llama-cpp-python

curl -sS -L -o dory-q5_k_m.gguf \
  "https://huggingface.co/nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-GGUF/resolve/main/NVIDIA-Nemotron-Labs-Dory1.0-4B-Q5_K_M.gguf"

sha256sum dory-q5_k_m.gguf
# => 96080be49ffd67b916018b7bdef8c484762576fb52780e10ab98ac4978a660e0 (モデルカード記載値と一致)

python3 -c "
from llama_cpp import Llama
Llama(model_path='dory-q5_k_m.gguf', n_ctx=512, verbose=True)
"
# => llama_model_load: error loading model: unknown model architecture: 'dory'
```

## ローカル検証が必要な項目(本Routine環境では未検証)

本Routineのクラウド実行環境は、外部ソースから取得した未レビューのコードをビルド・インストールする操作(`git clone`してきたリポジトリの`cmake`ビルド、`pip install git+https://...`)を安全ポリシー上ブロックしている。以下はそのため本Routine内では試行できなかった。**人間による手元PCでの再現を依頼したい。**

### (a) `transformers`をGitHub mainから入れて`dory`対応状況を確認

```bash
pip install -U "git+https://github.com/huggingface/transformers.git"
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
tok = AutoTokenizer.from_pretrained('nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16')
model = AutoModelForCausalLM.from_pretrained('nvidia/NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16', device_map='auto')
# config.n_recurrent_loops を 1 / 4 に変更して同一プロンプトで生成し、
# 出力トークン数・生成時間・回答内容を比較する
"
```

### (b) モデルカード記載のフォーク版llama.cppをビルドしてループ回数1/4のBefore/After比較

```bash
REV=98a74c97ea09ac72f6ceda1559808fc0a2f447ce
git clone https://github.com/brianchmielNV/llama.cpp.git llama.cpp-dory
git -C llama.cpp-dory fetch origin "$REV"
git -C llama.cpp-dory checkout --detach "$REV"

# CPU環境の場合(GGML_CUDA=ONはGPU必須。CPUのみならこのフラグは外す)
cmake -S llama.cpp-dory -B llama.cpp-dory/build \
  -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=OFF
cmake --build llama.cpp-dory/build --target llama-server --parallel

./llama.cpp-dory/build/bin/llama-server \
  -m dory-q5_k_m.gguf --alias dory --host 127.0.0.1 --port 8080 \
  --ctx-size 4096 --jinja --reasoning on \
  --override-kv "dory.num_loops=int:1,dory.recurrent_kv_cache_mode=str:per_loop"
# ↑ num_loops=1 と num_loops=4 のそれぞれで同一プロンプトを投げ、
#   出力トークン数・応答内容・生成時間を比較する(OpenAI互換API: http://127.0.0.1:8080/v1)
```

GPU(CUDA)がある場合はモデルカード記載の`-DGGML_CUDA=ON -DGGML_CUDA_GRAPHS=ON`付きビルドと`-ngl 999`を使う方が高速。

ダウンロード済みのGGUFファイル(SHA-256: `96080be49ffd67b916018b7bdef8c484762576fb52780e10ab98ac4978a660e0`)はこのRoutine環境には残らないため、ローカルで再取得が必要。

結果が出たら `results.md` と `articles/day-038-*.md` に反映する。

## ローカル検証(実施済み・2026-11-05)

人間のGPU環境(RTX 5060 Ti、CUDA 12.8)で上記(a)(b)を実際に試した。

- **(a) `transformers`をGitHub mainから入れ直す**: `pip install -U git+https://github.com/huggingface/transformers.git`でインストールしたバージョン(5.23.0.dev0)でも`AutoConfig.from_pretrained`は`KeyError: 'dory'` → `ValueError: ... does not recognize this architecture`で同じく失敗した。エラーメッセージが案内する回避策自体が、本検証時点のmainブランチではまだ機能していない。
- **(b) 専用フォーク版llama.cppのビルド**: `brianchmielNV/llama.cpp`のpin commitを`-DGGML_CUDA=ON`でビルドしたところ成功し、素のllama.cppでは失敗していた同じGGUFファイルのロードに成功した。ループ回数1と4のそれぞれでサーバーを起動し、同一プロンプト(算数の平均速度問題)で比較したところ、どちらも正解(60 km/h)にたどり着いたが、出力トークン数はほぼ同じ(1130 vs 1157)で、生成時間だけがループ回数4で約3.2倍(39.97秒→129.23秒)に伸びた。詳細は`results.md`の「6. ローカル検証」節を参照。
