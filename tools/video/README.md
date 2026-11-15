# 解説動画レンダラー(tools/video)

検証したシステムの仕組み・アーキテクチャを約1分で解説する、SNS用の縦型動画(1080x1920, 英語ナレーション+英語字幕)を作る。
デザイン・シーン構成・声は `render.py` に固定してあり、日ごとに変えるのは台本JSON(`posts/video/day-NNN.json`)だけ。

## 使い方

```bash
python3 -m venv .venv-video && .venv-video/bin/pip install -r tools/video/requirements.txt
.venv-video/bin/python tools/video/render.py posts/video/day-NNN.json --check          # 台本の検証と尺の見積もり
.venv-video/bin/python tools/video/render.py posts/video/day-NNN.json --stills /tmp/v  # シーンごとの静止画で見た目を確認
.venv-video/bin/python tools/video/render.py posts/video/day-NNN.json                  # 本番(mp4 + srt)
```

- 出力: `posts/video/day-NNN.mp4`(H.264 + AAC, 1〜2MB程度)と `posts/video/day-NNN.srt`(X等にアップロードできる字幕)。
- 声: Piperの `en_US-ljspeech-high`(学習データ LJ Speech はパブリックドメイン)。初回に約110MBを `~/.cache/ai100days/piper/` へ自動ダウンロードする。
  環境変数 `AI100_VOICE` で別の声に変えられるが、シリーズの統一のため変えない。CC BY-NC系の声(ryan, hfc_* 等)は使わない。
- ナレーションの尺が45〜75秒の範囲外だとエラーで止まる。台本を削って調整する(目安: 全体で120〜150語)。
- ffmpegはシステムのものを優先し、無ければ `imageio-ffmpeg` 同梱のものを使う。

## 固定フォーマット(5シーン、この順番のみ有効)

| # | type | 内容 | 目安 |
|---|---|---|---|
| 1 | `title` | Day番号・プロジェクト名・一行説明・ライセンス | 6〜8秒 |
| 2 | `overview` | 「What is it?」箇条書き2〜4個 | 8〜10秒 |
| 3 | `architecture` | 「How it works」ノード3〜8個の構成図。2〜4ステップで、ステップごとに注目するノードを光らせて説明 | 20〜28秒 |
| 4 | `finding` | 「What we found」今回の検証で分かったこと。大きな数字1つ+説明+任意で3行程度の端末風ブロック | 10〜14秒 |
| 5 | `outro` | Zenn記事(日本語)・出典・ライセンス・GitHubへの誘導 | 4〜6秒 |

## 台本JSONの書き方

見本: `posts/video/day-048.json`

```jsonc
{
  "day": 48,
  "project": "PyRIT",                 // タイトルに大きく出る名前
  "slug": "pyrit",                    // 上部の "$ day-048 / pyrit" 部分(短く)
  "tagline": "Microsoft's open-source red-teaming framework for generative AI",
  "source_url": "github.com/microsoft/PyRIT",   // https:// は付けない
  "license": "MIT",
  "scenes": [
    {"type": "title", "narration": "..."},
    {"type": "overview", "heading": "What is it?", "bullets": ["...", "..."], "narration": "..."},
    {"type": "architecture", "heading": "How it works",
     "nodes": [{"id": "a", "label": "Attack", "sub": "PromptSendingAttack", "pos": [0, 0], "span": 2}, ...],
     "edges": [{"from": "a", "to": "b", "label": "prompt"}, ...],
     "steps": [{"focus": ["a", "b"], "narration": "..."}, ...]},
    {"type": "finding", "heading": "What we found", "stat": "6 -> 3", "caption": "...",
     "lines": ["STRICT   T T T T T T", "..."], "narration": "..."},
    {"type": "outro", "narration": "..."}
  ]
}
```

- `pos` は `[列0〜2, 行0〜5]`。データの流れが上から下へ読めるように置く。`span: 2` で2列ぶち抜き。
- `label` は2〜3語、`sub` は実際のクラス名・コンポーネント名・モデル名(等幅で表示、長いと自動で縮小)。
- 横向きの矢印のラベルはボックスの上に出る。ラベルは短く(1〜3語)。
- `stat` の `->` は矢印として描画される。
- ナレーションは普通の英語で書く。`AI`, `API`, `LLM`, `JSON`, `7B` などの読み上げ方は `render.py` の `SAY` で自動変換され、字幕は元の表記のまま出る。

## 内容のルール

- 構成図は「そのツールの仕組み」を説明する。検証で実際に動かした構成(使ったモデル・接続先など)を `sub` に書いてよい。
- `finding` の数字・ログは `experiments/day-NNN/results.md` にある実際のものだけを使う。見栄えのために作らない・丸めすぎない。
- Routine環境の制約(ブラウザが無い、ダウンロードがブロックされた等)には触れない。
- 出典URLとライセンスを必ず入れる。

## フォント

`fonts/` にカードと同じ Fraunces / IBM Plex Sans / IBM Plex Mono(いずれも SIL Open Font License 1.1、ライセンス文同梱)を置いている。
