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

実行した8回(英語2回・日本語6回、入力は後述の公式サンプル音声)の「1フレームあたりの実測時間」:

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
