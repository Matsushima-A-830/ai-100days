---
title: "全二重音声対話モデルHaru-4BをCPUとGPUで動かしたら、GPUでは1フレーム133msを切ったが返事は毎回違った"
emoji: "🎙️"
type: "tech"
topics: ["ai", "speech", "llm", "python", "huggingface"]
published: false
---

## これは何を試した記事か

[higurashi-ai/Haru-4B](https://huggingface.co/higurashi-ai/Haru-4B)(Apache-2.0)を、コードとモデルを自前でダウンロードして実際に動かしてみた記事である。
Haru-4Bは「133msのフレームごとに、ユーザーの声を聞きながら自分の声とテキストを同時に生成する」全二重(フルデュプレックス)音声対話モデルである。
一般的なターンベースの音声アシスタントは「ユーザーが話し終わるのを待って」から応答を生成するが、Haru-4Bは聞き取りと発話を同じフレームで並行して行う設計になっている。

- 出典: https://huggingface.co/higurashi-ai/Haru-4B (Apache-2.0。2026-11-13公開)
- コード: https://github.com/higurashi-ai/Haru (Apache-2.0、検証コミット `7fe6b76`)
- Technical blog: https://blog.higurashi.ai/melte/haru4b/

Hugging Face Spacesのデモではなく、GitHubのコードをそのままインストールし、同梱のオフライン推論CLI `haru-inference` を使った。
モデルカードはNVIDIA GPU(12GB程度)を推奨しているので、GPUなしのCPUで動くかと、推奨どおりのGPUでどれくらい速いかの両方を測った。

## 検証環境

| 項目 | CPU環境A | ローカルPC(CPU / GPU) |
|---|---|---|
| CPU | Intel Xeon @2.10GHz、4コア | AMD Ryzen 7 7700、8コア16スレッド |
| GPU | なし | NVIDIA GeForce RTX 5060 Ti(16GB) |
| RAM | 15GB | 30GB |
| OS | Linux | Windows + WSL2(Ubuntu 24.04) |
| Python / torch | 3.11 / PyPIのデフォルトwheel | 3.12 / 2.11.0+cu128 |

## インストール(追加の有料APIキー不要)

GPUのPCでは、CUDA版のtorchを入れてから、Haruを `triton` extra付きで入れた。

```bash
$ git clone https://github.com/higurashi-ai/Haru
$ uv venv -p 3.12 .venv
$ uv pip install torch --index-url https://download.pytorch.org/whl/cu128
$ uv pip install -e "./Haru/haru[triton]"
$ .venv/bin/python -c "import torch,transformers;print(torch.__version__,torch.cuda.is_available(),torch.cuda.get_device_name(0),transformers.__version__)"
2.11.0+cu128 True NVIDIA GeForce RTX 5060 Ti 5.23.0
```

依存は `torch`・`transformers`・`tokenizers`・`safetensors`・`huggingface-hub` などの一般的なPythonパッケージだけで、有料APIキーの要求は無かった。
初回実行時に `model.safetensors`(約10.5GB)がHugging Face Hubから自動でダウンロードされ、筆者の回線では約2分だった。

## 入力は公式のサンプル音声

`hugging-apps/haru-4b` のSpaceが `gr.Examples` として配布している英語・日本語のサンプル音声(`en_seg.wav`・`ja_seg.wav`)と、声の参照音声(`en_ref.wav`・`ja_ref.wav`)を使った。
システムプロンプトには、リポジトリ内蔵の英語・日本語キャラクターカードを `haru.prompt.render_card` でテキスト化したものを渡した。
日本語は、Spaceの `app.py` と同じく末尾に5秒の無音を足した `ja_seg_padded.wav` も用意した。

## CPUでは動くが、リアルタイムの3倍以上遅い

`--device cpu` を渡すとCPUだけで推論できる。

```bash
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

CPU環境Aで英語・日本語あわせて9回実行し、1フレームあたりの実測時間は422.1〜462.1ms、平均は約435msだった。
ローカルPCのRyzen 7 7700でも、英語カード・seed=1で445.7ms/フレームとほぼ同じだった。

```bash
$ .venv/bin/haru-inference assets/en_seg.wav out/en_cpu_card_s1.wav --reference assets/en_ref.wav \
    --device cpu --transcript out/en_cpu_card_s1.jsonl --system-prompt-file card_en.txt --seed 1
...
75 frames (10.0 s), 445.7 ms per frame -> out/en_cpu_card_s1.wav
```

設計上の1フレームは133ms(7.5Hz)なので、CPUではリアルタイムの約3.2〜3.5倍遅い。
録音した音声を渡して結果を受け取るオフライン推論としては成立するが、ライブ会話には追いつかない。

## GPUでは1フレーム133msを下回った

同じコマンドを `--device cuda` にしてRTX 5060 Tiで実行した。

```bash
$ .venv/bin/haru-inference assets/en_seg.wav out/en_gpu_card.wav --reference assets/en_ref.wav \
    --device cuda --transcript out/en_gpu_card.jsonl --system-prompt-file card_en.txt
...
75 frames (10.0 s), 76.8 ms per frame -> out/en_gpu_card.wav
Haru
```

seedと言語を変えて計8回実行した。

| 実行(入力 / seed) | 1フレームの実測時間 | 出力テキスト |
|---|---|---|
| 英語 / -1 | 76.8 ms | "Haru" |
| 英語 / 1 | 95.7 ms | (無音) |
| 英語 / 7 | 104.9 ms | (テキストなし) |
| 英語 / 123 | 82.6 ms | "Hello" |
| 日本語(5秒無音追加) / 1 | 87.5 ms | "この山道を登りなげて" |
| 日本語(5秒無音追加) / 7 | 77.7 ms | "この年になって 自分には もう何の用もなかった。" |
| 日本語(5秒無音追加) / 123 | 87.0 ms | "人間は 山道を登る というよりも下るのである" |
| 英語 / 1 / `--codec-backend triton` | 72.5 ms | (無音) |

PyTorchのcodecでの7回の平均は約87.5ms/フレームで、133msの約0.66倍だった。
READMEで「GPU上で速くなる」とされているTriton codecにすると72.5ms/フレームになった(1回のみ)。
CPUと同じく `causal_conv1d`・`flash-linear-attention` は入れておらず、フォールバック実行の警告が出たままの数値である。

Webデモサーバーも起動してみた。

```bash
$ .venv/bin/haru-server --hf-repo higurashi-ai/Haru-4B --host 127.0.0.1 --port 8998
11:26:01 haru.server: serving on http://127.0.0.1:8998 (the model is loading)
11:26:06 haru.backends: loaded higurashi-ai/Haru-4B on cuda:0 in 6.7 s
11:26:09 haru.backends: warm-up: prompt of 593 positions in 1.8 s, then 86.1 ms per frame (a frame is 133 ms of audio)
11:26:09 haru.server: ready
```

モデルの読み込みは6.7秒で、warm-upでも86.1ms/フレームだった。
起動後のGPUメモリ使用量は13,592MiB(起動前は1,609MiB)で、モデルカードの「12GB程度」とおおむね合っていた。
ブラウザのマイクを使った実際の会話は今回試していない。

## 「話している最中に相づち」は毎回は起きなかった

全二重の挙動を見るため、出力テキストのフレームと、同じ区間のユーザー音声のRMS(音量)を突き合わせた。
RMSが0.01を超えるフレームを「ユーザーが話している最中」とみなした。

```python
data, sr = sf.read('assets/en_seg.wav')
frame = int(sr * 0.133)
# transcript_*.jsonl の各フレームのtextと、
# 同じフレーム区間のユーザー音声のRMSを比較する
```

CPU環境Aの英語カード・seed固定なしの実行では、ユーザーが話している最中のフレームに短い反応が乗っていた。

| 時刻 | ユーザー音声のRMS | ユーザーの状態 | モデルの発話 |
|---|---|---|---|
| 0.27s | 0.0205 | 話している最中 | "Sure" |
| 1.73s | 0.0586 | 話している最中 | " Oh" |
| 4.13s | 0.0040 | 静か | " that" |
| 4.27s | 0.0117 | 話している最中 | "'s" |
| 4.40s | 0.0678 | 話している最中 | " no" |
| 4.53s | 0.0889 | 話している最中 | " good" |

ところが、ほかの実行では様子がまったく違った。

| 実行 | テキストのあるフレーム | うちユーザー発話中 | 様子 |
|---|---|---|---|
| GPU 英語(5回) | 0〜2 | 0 | 無音か、冒頭0.40sに "Haru" / "Hello" の1語だけ |
| CPU 英語 seed=1(Ryzen) | 37 | 29 | ユーザーに重ねて自己紹介を話し続けた |
| GPU 日本語(3回) | 7〜16 | 0 | ユーザーが話し終えた後(8.38s以降)に話し始めた |

CPUのseed=1では、"Oh hi I'm Haru I'm twenty two years old I go running most mornings..." と、ユーザーの発話の上から自己紹介を続けていた。
GPUの日本語3回は、ユーザーの発話が8.38sで終わったあと、9.73s・9.87s・12.80sから話し始めていて、結果だけ見るとターン制に近い。
CPU環境Aの日本語では、seed固定なしの2回が無音、seed=1で「もし もし と」、seed=7で「こんにちは。」、seed=123で無音だった。
同じseedでもGPUとCPUで出力は一致しなかった。

聞きながら同時に話せる構造であることは、CPUのseed=1のように相手の発話に重ねて話し続けた例から分かる。
ただ、短い相づちを打つ、黙って聞く、話し終えてから答える、相手に重ねて話し続ける、のどれになるかは実行ごとに大きくばらついた。
1回の出力だけで「相づちを打つモデル」とも「反応しないモデル」とも言えないというのが、今回の結論である。

## まとめ

- Haru-4Bは、有料APIキーなしでインストールでき、GPUなしのCPUでも最後まで推論できた。
- CPUでは1フレーム(133ms)あたり約435〜446msで、リアルタイムの3倍以上遅い。
- RTX 5060 Ti(16GB)では72.5〜104.9ms/フレームで、オフライン推論では133msを下回った。GPUメモリは約12GBを使った。
- ユーザーの発話中に相づちを返した例はあったが、同じ入力でもseedやデバイスで「無音」「話し終えてから返答」「重ねて話し続ける」まで変わった。
- ブラウザのマイクを使ったリアルタイム会話は、Webデモサーバーの起動までで、会話そのものは確認していない。

## 出典・ライセンス

- モデル: https://huggingface.co/higurashi-ai/Haru-4B (Apache License 2.0)
- コード: https://github.com/higurashi-ai/Haru (Apache License 2.0)
- サンプル音声: https://huggingface.co/spaces/hugging-apps/haru-4b (`en_seg.wav` / `en_ref.wav` / `ja_seg.wav` / `ja_ref.wav`)
- 検証ログ: https://github.com/matsushima-a-830/ai-100days/tree/main/experiments/day-054
