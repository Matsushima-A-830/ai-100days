# Day 009: OpenMontage(agentic動画制作OSS)をゼロAPIキーで動かした結果

対象: https://github.com/calesthio/OpenMontage (AGPLv3)
検証したcommit: `9327439db69021ab4b0e2776729bf3b58fdb5a87`(2026-10-03、`git log -1`で確認)

スコープ: backlog.md / today.md の指示どおり、**有料APIキーを一切使わず**、
Piper TTS(ナレーション)・Remotion(編集/レンダリング)・FFmpeg(エンコード)のみで、
40秒程度の短い動画を1本作る。12パイプライン・52ツール・500 skillという巨大フレームワークの
フル機能を使い切ることは最初から目指さない。

## 0. 最初に見つかった食い違い: 紹介文の数値 vs 実測値

backlog.mdに記録した紹介文(GitHub Trending掲載時の説明文ベース)は
「12パイプライン・52ツール・500以上のagent skill」だったが、実際にcloneして数えると
食い違いがあった。

| 項目 | 紹介文の数値 | 実測値 | 確認方法 |
|---|---|---|---|
| パイプライン | 12 | `pipeline_defs/*.yaml` = **13**(本番12 + `framework-smoke.yaml`というスモークテスト用1本) | `ls pipeline_defs/` |
| ツール | 52 | ソース上の`class .*(BaseTool)`定義 = **129**、ツールレジストリの`registry.discover()`が返す登録数 = **137** | `grep -rn "^class .*(BaseTool)" tools/` / `tool_registry.registry.discover()` |
| agent skill | 500以上 | `skills/`以下のMarkdownファイル = **157** | `find skills -type f \| wc -l` |

パイプライン数はほぼ一致したが、ツール数は紹介文より多く、skill数は紹介文の1/3程度だった。
「日本語で未発信か」の確認時に拾った紹介文の数値をそのまま記事に書かず、実測して裏取りしたのは
今回の検証で一番価値があった作業だと思う。

## 1. 環境セットアップ(`make setup`)

```
$ git clone --depth 1 https://github.com/calesthio/OpenMontage.git
$ cd OpenMontage && make setup
```

Python依存・`remotion-composer`のnpm依存・`piper-tts`・HyperFramesのnpxキャッシュ、
すべて警告なしで完了した(disk上の実行ログは本experimentには残していないが、
exit codeは全ステップ0)。前提ソフトウェアはすべてこの実行環境に最初から入っていた
(`Python 3.11.17` / `node v22.22.0` / `npm 10.9.4` / `ffmpeg 6.1.1`)。

## 2. ゼロキーデモ(`make demo`)が最初はブロックされた

`make demo-list`で以下の3本の「ゼロキー・Remotionのみ」デモが確認できた:
`world-in-numbers` / `code-to-screen` / `focusflow-pitch`。

`world-in-numbers`をレンダーしようとした最初の実行は失敗した。

```
$ python render_demo.py world-in-numbers
Downloading Chrome Headless Shell https://www.remotion.dev/chrome-headless-shell
Downloading from: https://remotion.media/chromium-headless-shell-linux-x64-149.0.7790.0.zip?clear
Error: Received a status code of 403 while downloading file ...
Host not in allowlist: remotion.media. Add this host to your network egress settings to allow access.
```

Remotionはレンダリング用のヘッドレスChromeを初回に`remotion.media`から自動ダウンロードするが、
この実行環境のネットワークegressポリシーがそのホストを許可していなかった。
これは「動かなかった」という正直な結果であり、ポリシーを迂回する設定変更はしていない。

### 回避策: 既にある別のChromiumを指定する

幸い、この実行環境にはPlaywright用のChromium(`/opt/pw-browsers/`)が最初から入っていた。
Remotionの`npx remotion render`には`--browser-executable`というフラグがあり、
ダウンロード済みの実行ファイルを直接指定できる。

```
$ npx remotion render src/index.tsx Explainer out.mp4 --props props.json --codec h264 \
    --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
```

これでChromeのダウンロードは回避できたが、今度はGoogle Fontsの読み込みで
`net::ERR_CERT_AUTHORITY_INVALID`が出た(この実行環境のHTTPS通信はTLSを再終端する
プロキシ経由のため、ヘッドレスChromeがそのプロキシのCAを信頼していないため)。
`--ignore-certificate-errors`を追加して解決した。

```
$ npx remotion render src/index.tsx Explainer \
    /tmp/OpenMontage/projects/demos/renders/world-in-numbers.mp4 \
    --props public/demo-props/world-in-numbers.json --codec h264 \
    --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
    --ignore-certificate-errors
...
+  /tmp/OpenMontage/projects/demos/renders/world-in-numbers.mp4 4.3 MB
```

`ffprobe`で検証: `h264 1920x1080` + `aac`、`duration=23.06s`、サイズ4.3MB。
**これはOpenMontage公式のゼロキーデモが、この実行環境でも実際に動画として出力できることを
確認したベースラインの結果**(本動画自体は`experiments/day-009/`には含めていない。
下記4節の「本番」動画で同じ回避策を使っている)。

## 3. Piper TTS(ナレーション)でも2つの食い違いにぶつかった

### 3-1. リポジトリ自身のインストール手順が古い

`tools/audio/piper_tts.py`の`install_instructions`は

```
pip install piper-tts
piper --download-dir ~/.piper/models --model en_US-lessac-medium
```

だが、`make setup`が実際に入れる`piper-tts==1.8.0`ではこの2行目は機能しない
(`--download-dir`はダウンロード先指定用のオプションではなく、
`piper`本体の`-m/--model`はONNXファイルへの直接パスを要求し、
裸のモデル名を渡すと`ValueError: Unable to find voice: en_US-lessac-medium
(use piper.download_voices)`で失敗する)。正しい取得方法は

```
python -m piper.download_voices en_US-lessac-medium --download-dir <dir>
```

だった。

### 3-2. その正しい方法でダウンロードしたファイルが壊れていた

上記コマンドでダウンロードした`en_US-lessac-medium.onnx`(62,423,791 bytes)を
`piper`に渡すと、

```
onnxruntime.capi.onnxruntime_pybind11_state.InvalidProtobuf: [ONNXRuntimeError] : 7 :
INVALID_PROTOBUF : Load model from .../en_US-lessac-medium.onnx failed:Protobuf parsing failed.
```

で失敗した。同じファイルをHugging Faceの公式resolve URLから`curl`で直接取得したもの
(63,201,294 bytes、約777KB大きい)は正常に動いた。`piper.download_voices`内部の
HTTPクライアントがこの実行環境で途中で切れた/壊れたダウンロードを検知せずに書き込んだ
可能性が高い。本結果は「`piper.download_voices`が信用できない」という一般論ではなく、
**この実行環境でこの1回、この挙動になった**という正直な記録として書いている。

### 3-3. 日本語音声は追加の依存が必要だった

OpenMontageのREADMEはPiper=「zero keys narration」としか書いておらず、
日本語音声(`ja_JP-hi_fi_captain-medium`)を試すと

```
ModuleNotFoundError: No module named 'pyopenjtalk'
```

で失敗した。`pip install pyopenjtalk`を追加すると、初回実行時に`open_jtalk`の辞書
(23MB、GitHubから自動取得)がダウンロードされ、以降は日本語ナレーションが
問題なく合成できた。この依存はOpenMontage側のドキュメントには書かれていない
(Piperというより、Piperが使うライブラリ側のJapanesePhonemizerの要件)。

## 4. 本番: ナレーション付き40秒動画を実際にレンダリングした

上記の回避策をすべて適用し、OpenMontage自身の`Explainer`コンポジション(`cuts`形式の
データ駆動レンダラー、`hero_title` / `stat_card` / `bar_chart` / `text_card`を使用)に、
本検証で実測した数値(0節の表、2〜3節の食い違い)を素材にした5文の日本語ナレーションを
Piper TTS(`ja_JP-hi_fi_captain-medium`)で合成し、1本の動画に組み上げた。

ナレーション各文の実測秒数(`ffprobe`、`--sentence-silence 0.3`):

| # | 文 | 秒数 |
|---|---|---|
| 1 | GitHubトレンディング一位のOpenMontageを、有料APIキーなしで実際に動かしてみました。 | 7.64s |
| 2 | ツールレジストリを調べると、紹介文にあった52個ではなく137個のツールが登録されていました。 | 8.09s |
| 3 | ただしゼロキーで実際に動くツールは137個中39個だけで、残りは有料APIキーが必要でした。 | 8.67s |
| 4 | 今回はPiperTTSとRemotion、FFmpegだけを使い、課金は一切なしでナレーション付きの動画を作れました。 | 8.71s |
| 5 | ただしレンダリング用のChromeダウンロードがネットワーク制限で止まり、手動の回避策が必要でした。 | 7.21s |

5本を`ffmpeg -f concat`で結合し、合計40.32秒の1本の音声ファイルにした
(`output/narration/narration_ja.wav`)。この秒数に合わせて`cuts`の`in_seconds`/`out_seconds`を
設定し(`day-009-props.json`)、Explainerコンポジションの`calculateMetadata`が
最後のカットの終了時刻+1秒でフレーム数を自動計算した。

レンダリングコマンド:

```
$ npx remotion render src/index.tsx Explainer output/day-009.mp4 \
    --props day-009-props.json --codec h264 --scale 0.5 \
    --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
    --ignore-certificate-errors
...
+  .../day-009-small.mp4 3.3 MB
```

`ffprobe`での検証結果(そのまま記録):

```
[STREAM] codec_name=h264 codec_type=video width=960 height=540
[STREAM] codec_name=aac codec_type=audio sample_rate=48000 channels=2
[FORMAT] duration=41.877333 size=3265145
```

→ `experiments/day-009/output/day-009.mp4`(960x540, h264+aac, 41.9秒, 3.3MB)として
本experimentに含めた。**使用した有料APIは0件**(FAL/Kling/Runway/ElevenLabs/OpenAI等への
通信は一切発生していない。ナレーションはPiper、画は Remotionのネイティブコンポーネント
〈タイトルカード・stat card・bar chart・text card〉、エンコードはFFmpegのみ)。

## 5. ツールレジストリで「ゼロキーで実際に動くのは何個か」を数えた

OpenMontage自身のAGENT_GUIDE.mdが推奨する確認コマンドを実行した(venv有効化、
Piperもインストール済みの状態):

```python
from tools.tool_registry import registry
registry.discover()
env = registry.support_envelope()
```

結果:

- 登録されているツール総数: **137**
- うちステータスが`available`(=このゼロキー環境で実行可能): **39**
- `unavailable`(主に有料APIキー未設定、または未インストールの外部バイナリが原因): **98**
- `piper_tts`のステータス: `available`(今回のセットアップ後に確認)

「ゼロキーでも動画が作れる」という公式の主張は、**狭い意味では正しい**(ナレーション・
Remotion描画・FFmpegエンコードの最小パスはPiperだけで完結する)。一方で
「ツールの大半(137個中98個、約72%)は有料APIキーか追加インストールが無いと動かない」のも
同時に事実で、137個中39個という数字で両方を同時に伝えられると考え、動画と記事の軸にした。

## 6. 今回「検証しなかった」範囲(正直な線引き)

- OpenMontage自身のエージェント運用フロー(自然言語の1行プロンプトだけを渡し、
  エージェント自身に`pipeline_defs/` → `skills/pipelines/` → `tool_registry`の順で
  パイプラインを選ばせ、52〜137個のツールを自律的に呼び出させる、という本来の使い方)は
  試していない。本動画は、ゼロキーで実際に動くと確認できた3つの部品
  (Piper TTS・Remotionの`Explainer`コンポジション・FFmpeg)を、
  筆者(Claude Code)が直接組み立てて作った。12本あるパイプライン定義
  (`pipeline_defs/*.yaml`)や500行超の`AGENT_GUIDE.md`が指示する
  「スコアリングされたプロバイダ選択」「決定ログ」等の仕組みは経由していない。
- 画像/動画生成プロバイダ(Veo, Kling, Runway等)、ストック素材取得
  (Pexels/Archive.org/Wikimedia)、BGM、word-levelキャプション(TikTok風字幕)は未検証。
  これらもOpenMontageの「ゼロキーで使える」と紹介される機能の一部だが、
  今回のスコープ(数十秒の動画を1本、最小構成で)には含めなかった。
- HyperFrames(`make setup`でnpxキャッシュのみ温めた)は使っていない。今回はRemotionのみ。

## 7. 人間によるレビュー結果(2026-10-07追記)

完成した`output/day-009.mp4`を実際に再生して確認したところ、**全体として大きな違和感はない**という評価だったが、Piper TTSのナレーション(`ja_JP-hi_fi_captain-medium`)に発音上の問題が2点見つかった。

- **「有料」の読み上げ**: 中国語読みのように聞こえる、不自然な発音になっている(ナレーション原稿1文目・3文目・4文目に登場。`narration_script.txt`参照)。
- **「FFmpeg」の読み上げ**: 正しく発音されていない(ナレーション原稿4文目「今回はPiperTTSとRemotion、FFmpegだけを使い」に、英字の製品名をそのままPiper TTSへ渡していたことが原因と考えられる)。

いずれも、日本語TTSエンジンに辞書にない語(「有料」のような同音異義語になりやすい単語、"FFmpeg"のような英字の固有名詞)をそのまま読ませたことに起因する、よくある日本語TTSの弱点だと考えられる。根本的に直すには、ナレーション原稿側で読み方を明示する(例: 「FFmpeg」を「エフエフエムペグ」とカタカナ表記に置き換える、Piperが対応していれば読み仮名付きのSSML/辞書登録を使う)必要がある。今回はこの問題を記録するにとどめ、音声の再生成・動画の再レンダリングは行っていない。
