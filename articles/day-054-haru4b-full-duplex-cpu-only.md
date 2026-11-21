---
title: "全二重音声対話モデルHaru-4Bを、GPUなしのCPUだけで動かしてみた"
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
- コード: https://github.com/higurashi-ai/Haru (Apache-2.0)
- Technical blog: https://blog.higurashi.ai/melte/haru4b/

今回は、公開されているHugging Face Spacesのデモを使わず、GitHubのコードをそのままインストールして、自分のマシン(厳密には検証に使ったコンテナ環境)で素のPython APIを直接叩いた。
モデルカードはNVIDIA GPU(12GB程度)を推奨しているが、手元の環境にGPUが無かったため、まず「CPUだけで本当に動くのか」を確かめることにした。

## 筆者の環境

| 項目 | 内容 |
|---|---|
| CPU | Intel Xeon @2.10GHz、4コア |
| GPU | なし |
| RAM | 15GB |
| Python | 3.11 |
| torch | PyPIのデフォルトwheel(CPU/CUDA同梱) |

## インストール(成功、追加の有料APIキー不要)

```bash
git clone https://github.com/higurashi-ai/Haru
python3 -m venv .venv
.venv/bin/pip install torch
.venv/bin/pip install -e ./Haru/haru
```

`torch`・`transformers`・`tokenizers`・`safetensors`・`huggingface-hub`といった一般的なPythonパッケージのみで、モデルカードに書かれた以外の依存は無かった。
有料APIキーの要求も一切無い。

## CPUでの推論は動いたが、リアルタイムの3.2〜3.5倍遅かった

リポジトリには`haru-inference`というオフライン推論用のCLIが同梱されており、`--device cpu`を渡すだけでCPU実行に切り替えられる。
`hugging-apps/haru-4b`のHugging Face Spaceが配布している公式サンプル音声(`en_seg.wav`・`en_ref.wav`)を使い、同じリポジトリ内蔵の英語キャラクターカードをシステムプロンプトにして実行した。

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

モデルの読み込みから推論まで、エラーで落ちることなく最後まで動いた。
英語・日本語あわせて8回実行した「1フレームあたりの実測時間」の平均は約435msだった。
Haru-4Bは設計上1フレームが133ms(7.5Hz)なので、このCPU環境ではリアルタイムの約3.2〜3.5倍遅いということになる。
つまり「動かすこと自体」はGPUなしでも可能だが、ライブの会話として実時間で聞き取り・発話するには全く追いつかない。
`causal_conv1d`・`flash-linear-attention`という最適化カーネルが入っていないフォールバック実行だという警告が出ており、これらのカーネルとGPUがあれば数値は変わるはずだが、それは未検証である。

## 「話し終わるのを待たない」が実際に確認できた

Haru-4Bの売りである全二重の挙動を、出力テキストと入力音声の音量を突き合わせて確認した。

```python
data, sr = sf.read('assets/en_seg.wav')
frame = int(sr * 0.133)
# transcript_en_cpu_card.jsonl の各フレームのtextと、
# 同じフレーム区間のユーザー音声のRMS(音量)を比較する
```

| 時刻 | ユーザー音声のRMS | ユーザーの状態 | モデルの発話 |
|---|---|---|---|
| 0.27s | 0.0205 | 話している最中 | "Sure" |
| 1.73s | 0.0586 | 話している最中 | " Oh" |
| 4.13s | 0.0040 | 静か | " that" |
| 4.27s | 0.0117 | 話している最中 | "'s" |
| 4.40s | 0.0678 | 話している最中 | " no" |
| 4.53s | 0.0889 | 話している最中 | " good" |

ユーザーの音量が高い、つまり実際に話している最中のフレームで、モデルが"Sure"や"Oh"、"that's no good"といった相づち的な発話を生成している。
「ユーザーが話し終わるのを待ってから応答する」のではなく、相手がまだ話している間に割り込み的な反応が生成されており、全二重という設計上の特徴が実際の出力でも確認できた。

## 日本語ではseedによって挙動が大きく変わった

同じ手順を公式の日本語サンプル音声(`ja_seg.wav`・`ja_ref.wav`)と日本語キャラクターカードで試したところ、乱数シードを固定しないデフォルト設定では2回とも無音(テキストなし)だった。
モデルが「聞くだけ」で終わるのも全二重の設計上あり得る挙動だが、本当に無言なのか乱数の巡り合わせなのかを確かめるため、シードを固定して3回試した。

| seed | 出力テキスト |
|---|---|
| 1 | "もし もし と"(「もしもし」=電話の呼びかけの相づち) |
| 7 | "こんにちは。" |
| 123 | (無音。テキストなし) |

3回のうち2回は相づち的な短い日本語が生成されたが、1回は無音だった。
デフォルト設定の1回限りの実行では「何も言わない」結果に当たることもあり、日本語で試す場合は何度か繰り返さないと全二重らしい反応に出会いにくいかもしれない。

## まとめ

- Haru-4Bは、モデルカードが推奨するGPUが無くても、CPUだけでロード・推論できた。
- ただし1フレーム(133ms)あたり平均435ms、リアルタイムの3.2〜3.5倍遅く、ライブ会話には全く追いつかない。
- ユーザーがまだ話している最中に相づち的な発話が生成されることを、音声の音量と出力テキストの時刻を突き合わせて確認できた。これは一般的なターンベースの音声アシスタントには無い挙動である。
- 日本語では、同じ入力・同じプロンプトでも乱数シードによって「相づちを返す」か「無言のまま」かが変わった。

ライブのマイク入力を使った実際の低遅延会話(`python -m haru.server`をGPU搭載PCで起動するもの)は、今回の環境では確認できていない。

## 出典・ライセンス

- モデル: https://huggingface.co/higurashi-ai/Haru-4B (Apache License 2.0)
- コード: https://github.com/higurashi-ai/Haru (Apache License 2.0)
- サンプル音声: https://huggingface.co/spaces/hugging-apps/haru-4b (`en_seg.wav` / `en_ref.wav` / `ja_seg.wav` / `ja_ref.wav`)
- 検証ログ: `experiments/day-054/`
