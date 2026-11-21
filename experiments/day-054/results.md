# Day 054 検証結果: higurashi-ai/Haru-4B

出典: https://huggingface.co/higurashi-ai/Haru-4B (Apache-2.0)
Code: https://github.com/higurashi-ai/Haru (Apache-2.0。検証に使ったコミットは `git clone` 直後の2026-11-21時点のmain)
Technical blog: https://blog.higurashi.ai/melte/haru4b/ / https://blog.higurashi.ai/melte/haru4b-ja/

## 0. 何を検証したか

Haru-4Bは「133msフレームごとに、ユーザーの声を聞きながら自分の声とテキストを同時に生成する」全二重音声対話モデルである。
公開Hugging Face Spaces(`hugging-apps/haru-4b`)はZeroGPU上で動くオフラインデュプレックスデモだが、
このRoutine実行環境のネットワークポリシーでは `*.hf.space` ドメイン(Spacesの実行ホスト)への接続が
エージェントプロキシにブロックされており(`403 Forbidden: no rule or network setting allows this host`)、
Spaces経由での検証はできなかった。これはRoutine実行環境固有のネットワーク制約であり、記事本文には書かない
(試行ログは `test_haru.py` / `raw_results.json` に残す)。

そこで方針を変え、GitHubリポジトリ(`higurashi-ai/Haru`)を素のPython APIとして**自前ホストする側**を検証した。
`huggingface.co`(モデル本体のダウンロード)と`github.com`(コードのクローン)はこのRoutine環境から到達できたため、
このRoutine実行環境自体(GPUなし、CPU 4コア、Intel Xeon @2.10GHz、RAM 15GB)でCPUのみの推論を実際に試した。

## 1. インストール(成功、追加の有料APIキー不要)

```
$ git clone --depth 1 https://github.com/higurashi-ai/Haru
$ python3 -m venv .venv && .venv/bin/pip install torch  # CPU環境、PyPIのデフォルトwheel
$ .venv/bin/pip install -e ./Haru/haru
```

`torch`・`transformers`・`tokenizers`・`safetensors`・`huggingface-hub`等、モデルカードに書かれた以外の
依存は無く、有料APIキーの要求も一切無かった。

## 2. CPUでの自前ホスト推論(成功。ただしリアルタイムの3.2〜3.5倍遅い)

モデルカードはNVIDIA GPU(12GB程度)を推奨しているが、`haru-inference`はCLIに`--device cpu`を渡せる。
実際にCPUだけで実行すると、**モデルの読み込み・推論そのものは動いた**(途中で落ちたりエラーにはならなかった)。

```
$ .venv/bin/haru-inference assets/en_seg.wav out_en_cpu_card.wav \
    --reference assets/en_ref.wav --device cpu \
    --transcript transcript_en_cpu_card.jsonl \
    --system-prompt-file card_en.txt
...
[transformers] `causal_conv1d_fn` is falling back to its reference PyTorch implementation because
`causal_conv1d` is not installed. This is correct but much slower; ...
[transformers] `chunk_gated_delta_rule` is falling back to its reference PyTorch implementation
because `flash-linear-attention` is not installed. This is correct but much slower; ...
75 frames (10.0 s), 428.9 ms per frame -> out_en_cpu_card.wav
Sure  Oh  that's no good
```

実行した9回(英語2回・日本語7回、入力は後述の公式サンプル音声)の「1フレームあたりの実測時間」:

| 実行 | 1フレームの実測時間 |
|---|---|
| 英語(簡易プロンプト) | 441.5 ms |
| 英語(公式カード) | 428.9 ms |
| 日本語(簡易プロンプト) | 447.8 ms |
| 日本語(公式カード) | 423.3 ms |
| 日本語(speak_first, seed=42) | 430.6 ms |
| 日本語(5秒無音追加, seed=-1) | 422.1 ms |
| 日本語(5秒無音追加, seed=1) | 462.1 ms |
| 日本語(5秒無音追加, seed=7) | 423.1 ms |
| 日本語(5秒無音追加, seed=123) | 436.2 ms |

(注: seed=1/7/123の3回は出力音声・文字起こし(`out_ja_seed_*.wav` / `transcript_ja_seed_*.jsonl`)のみが残っており、標準出力ログは `logs/` にコミットされていない。2026-11-21のローカル検証時点で確認。)

平均は約**435ms/フレーム**。モデルの設計上1フレームは133ms(7.5Hz)なので、
CPU(4コア, Intel Xeon @2.10GHz)では**リアルタイムの約3.2〜3.5倍遅い**。
つまり「読み込んで動かす」こと自体はGPUなしでも可能だったが、
ライブの会話として実時間で聞き取り・発話するにはこのCPU環境では全く追いつかない。
`causal_conv1d`・`flash-linear-attention`という最適化カーネルが入っていないフォールバック実行である
という警告が出ており、GPU+これらのカーネルがあれば数値は変わるはずだが、それは未検証。

## 3. 全二重(同時聞き取り・発話)の実際の挙動

英語サンプル(公式カードプロンプト使用)の出力テキストを、入力音声のRMS(音量)と時刻で突き合わせた。

```python
# experiments/day-054/ で実行
data, sr = sf.read('assets/en_seg.wav')
frame = int(sr * 0.133)
# transcript_en_cpu_card.jsonl の各フレームの text と、同じフレーム区間のuser音声のRMSを比較
```

結果:

| 時刻 | ユーザー音声のRMS | ユーザーの状態 | モデルの発話(テキスト) |
|---|---|---|---|
| 0.27s | 0.0205 | 話している最中 | "Sure" |
| 1.73s | 0.0586 | 話している最中 | " Oh" |
| 4.13s | 0.0040 | 静か | " that" |
| 4.27s | 0.0117 | 話している最中 | "'s" |
| 4.40s | 0.0678 | 話している最中 | " no" |
| 4.53s | 0.0889 | 話している最中 | " good" |

**ユーザーの音声レベルが高い(=実際に話している)フレームでモデルが"Sure"や"Oh"、"that's no good"と相づち・反応を
発している。** つまり「ユーザーが話し終わるのを待ってから応答する」のではなく、ユーザーがまだ話している最中に
相づち的な発話が生成されており、全二重という設計上の特徴が実際の出力でも確認できた。
これは一般的なターンベースの音声アシスタント(ユーザーの発話終了を検知してから応答を生成する)とは
明確に異なる挙動である。

全文の文字起こし(英語、公式カード使用): `"Sure Oh that's no good"`

## 4. 日本語での挙動には強いばらつきがあった

日本語サンプル(`ja_seg.wav`、公式日本語カード使用)では、デフォルト設定(`seed=-1`、毎回ランダム)だと
**2回とも無音(テキストなし)** だった。モデルが「聞くだけ」で終わることも全二重の設計上あり得るが、
本当に何も言わないのか、単に乱数の巡り合わせなのかを確かめるため、`--seed`を固定して3回試した。

| seed | 出力テキスト |
|---|---|
| 1 | "もし もし と"(「もしもし」=電話の呼びかけの相づち的反応) |
| 7 | "こんにちは。" |
| 123 | (無音。テキストなし) |

つまり日本語でも相づち的な短い発話は実際に生成されるが(3回のうち2回)、デフォルト(乱数シード固定なし)の
1発実行や一部のシードでは「何も言わない」結果になることもあり、公開Spacesのデモで日本語を触った場合、
何回か試さないと全二重らしい割り込み・相づちには出会いにくい可能性がある。

## 5. 使った入力音声について

`assets/en_seg.wav` / `assets/en_ref.wav` / `assets/ja_seg.wav` / `assets/ja_ref.wav` は、
公開Space `hugging-apps/haru-4b`(https://huggingface.co/spaces/hugging-apps/haru-4b)が
`gr.Examples`として配布している実例音声をそのまま使った
(`https://huggingface.co/spaces/hugging-apps/haru-4b/resolve/main/assets/en_seg.wav` 等から取得)。
自作の音声ではなく、モデル配布元が「これで試してください」と示している公式サンプルである。

## 6. ローカル検証への引き継ぎ

- GPU(モデルカード推奨の12GB NVIDIA GPU)での実際のリアルタイム会話(マイク入力・低遅延)は、
  このRoutine実行環境にGPUが無いため未検証。`python -m haru.server --hf-repo higurashi-ai/Haru-4B`
  (http://localhost:8998 でブラウザから対話)をGPU搭載PCで実行すると試せる。
- 公開Spaces(`hugging-apps/haru-4b` / `akhaliq/haru-4b-studio`)経由の検証は、このRoutine環境の
  ネットワークポリシーで`*.hf.space`への接続がブロックされたため未実施(ローカルPCのブラウザからであれば
  問題なく開けるはずである)。

## 7. ローカル検証(2026-11-21, matsu PC)

環境: Windows + WSL2(Ubuntu 24.04、Linux 6.6)、CPU AMD Ryzen 7 7700(8コア16スレッド)、RAM 30GB、
GPU NVIDIA GeForce RTX 5060 Ti(16GB)、Python 3.12、torch 2.11.0+cu128、transformers 5.23.0、
Haru commit `7fe6b7665f8bf035998f401f8cb779fbe53f2751`(2026-11-13)。
`causal_conv1d` / `flash-linear-attention` は未導入(CPU検証と同じフォールバック警告が出る状態)。
入力・カードは本ディレクトリの `assets/` / `card_en.txt` / `card_ja.txt` をそのまま使った。
ログは `logs/07`〜`16`、出力音声・文字起こしは `local/out/`、実行スクリプトは `local/run_batch.sh`。

### 7-1. インストール

```
$ uv venv -p 3.12 .venv
$ uv pip install torch --index-url https://download.pytorch.org/whl/cu128
$ uv pip install -e "./Haru/haru[triton]"
$ .venv/bin/python -c "import torch,transformers;print(torch.__version__,torch.cuda.is_available(),torch.cuda.get_device_name(0),transformers.__version__)"
2.11.0+cu128 True NVIDIA GeForce RTX 5060 Ti 5.23.0
```

モデル(`model.safetensors` 約10.5GB)のダウンロードは約2分(`Fetching 3 files: 100% 3/3 [02:06<00:00]`)。

### 7-2. GPUでは1フレームが133msを下回った

```
$ .venv/bin/haru-inference assets/en_seg.wav out/en_gpu_card.wav --reference assets/en_ref.wav \
    --device cuda --transcript out/en_gpu_card.jsonl --system-prompt-file card_en.txt
...
75 frames (10.0 s), 76.8 ms per frame -> out/en_gpu_card.wav
Haru
```

| 実行(device / 入力 / seed) | 1フレームの実測時間 | 出力テキスト |
|---|---|---|
| GPU / 英語カード / seed=-1 | 76.8 ms | "Haru" |
| GPU / 英語カード / seed=1 | 95.7 ms | (無音) |
| GPU / 英語カード / seed=7 | 104.9 ms | (テキストなし) |
| GPU / 英語カード / seed=123 | 82.6 ms | "Hello" |
| GPU / 日本語カード・5秒無音追加 / seed=1 | 87.5 ms | "この山道を登りなげて" |
| GPU / 日本語カード・5秒無音追加 / seed=7 | 77.7 ms | "この年になって 自分には もう何の用もなかった。" |
| GPU / 日本語カード・5秒無音追加 / seed=123 | 87.0 ms | "人間は 山道を登る というよりも下るのである" |
| GPU / 英語カード / seed=1 / `--codec-backend triton` | 72.5 ms | (無音) |
| CPU(Ryzen 7 7700) / 英語カード / seed=1 | 445.7 ms | "Oh hi I'm Haru I'm twenty two years old I go running most mornings It's good for my brain and it clears my head I also am very curious about lot of things" |

- GPU(PyTorch codec)7回の平均は約87.5ms/フレームで、設計上の133msの約0.66倍。リアルタイムより速い。
- Triton codecでは72.5ms/フレーム(1回のみ)。
- CPU(Ryzen 7 7700)は445.7ms/フレームで、セクション2のXeon 4コアの結果(平均約435ms)とほぼ同じ。リアルタイムの約3.4倍遅い。
- GPU実行時のプロセス最大RSSは約13.4GB(`/usr/bin/time`)、Webデモ起動後のGPUメモリ使用量は13,592MiB(起動前1,609MiB)。
- 同じseedでもGPUとCPUでは出力が異なった(例: 英語seed=1はGPUで無音、CPUで長い自己紹介)。

### 7-3. Webデモサーバーの起動

```
$ .venv/bin/haru-server --hf-repo higurashi-ai/Haru-4B --host 127.0.0.1 --port 8998
11:26:01 haru.server: serving on http://127.0.0.1:8998 (the model is loading)
11:26:06 haru.backends: loaded higurashi-ai/Haru-4B on cuda:0 in 6.7 s
11:26:09 haru.backends: warm-up: prompt of 593 positions in 1.8 s, then 86.1 ms per frame (a frame is 133 ms of audio)
11:26:09 haru.server: ready
$ curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8998/
HTTP 200
```

サーバーの起動とwarm-upまでは確認した。ブラウザのマイクを使った実際の会話は試していない。

### 7-4. 出力テキストとユーザー音声の重なり(`local/overlap.py`、結果は `local/overlap-results.txt`)

セクション3と同じく、フレームごとのユーザー音声RMSが0.01を超えるかで「話している最中」を判定した。
ユーザー音声は英語0.0〜9.84s、日本語0.0〜8.38sに発話がある(日本語は末尾に5秒の無音を追加)。

| 実行 | テキストのあるフレーム | うちユーザー発話中 |
|---|---|---|
| GPU 英語 seed=-1 / 1 / 7 / 123 / triton | 2 / 0 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 |
| CPU 英語 seed=1 | 37 | 29 |
| GPU 日本語 seed=1 / 7 / 123 | 7 / 12 / 16 | 0 / 0 / 0 |

- GPUの英語5回は、無音か冒頭0.40sの1語("Haru" / "Hello")だけで、ユーザー発話中のテキストは無かった。
- CPUの英語seed=1は、ユーザーが話している間も自己紹介を話し続けた(37フレーム中29フレームが発話中)。
- GPUの日本語3回は、いずれもユーザーが話し終えた後(9.73s / 9.87s / 12.80s開始)の無音区間で話した。
- つまり「ユーザーの発話中に短い相づちを返す」挙動はセクション3の1例(CPU, seed=-1)以外では再現せず、
  実行(seed・デバイス)によって「黙って聞く」「話し終えてから答える」「相手の発話に重ねて話し続ける」まで大きくばらついた。

### 7-5. PRの記述との差分

- PRの「CPUではリアルタイムの約3.2〜3.5倍遅い」は、別CPU(Ryzen 7 7700)でも445.7ms/フレームで再現した。
- GPU(RTX 5060 Ti 16GB)では72.5〜104.9ms/フレームで、オフライン推論ではリアルタイムより速く動いた。
- 「話している最中に相づちを返す」はセクション3の1回で観測されたものであり、毎回起きる挙動ではなかった。
- 実行回数は9回(PR時点の記事・X投稿・カード・動画の「8回」は誤り)。
