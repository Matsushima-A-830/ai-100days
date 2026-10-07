# Day 009: OpenMontageをゼロAPIキーで動かす

対象: https://github.com/calesthio/OpenMontage (AGPLv3)、検証commit `9327439db6902...`

詳しい経緯・つまずき・実測値は `results.md` を参照。ここでは再現手順のみをまとめる。

## 再現手順

OpenMontage本体はAGPLv3のOSSであり、サイズが大きいため本リポジトリには含めていない。
別途cloneして以下の手順で再現する。

```bash
# 1. 本体を取得してセットアップ(ネットワーク接続が必要)
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup   # Python依存 / remotion-composerのnpm依存 / piper-tts / HyperFramesキャッシュ

# 2. レンダリング用ブラウザの回避策(results.md 2節参照)
#    この環境ではRemotionの自動Chromeダウンロード先(remotion.media)がブロックされるため、
#    既存のPlaywright用Chromium(環境によりパスは異なる)を明示的に指定する。
#    --ignore-certificate-errors はTLS再終端プロキシ環境でのフォント読み込みエラー回避に必要。
BROWSER=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell

# 3. 日本語ナレーション用の追加セットアップ(results.md 3-3節参照)
.venv/bin/python -m pip install pyopenjtalk
curl -L -o ja_JP-hi_fi_captain-medium.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/ja/ja_JP/hi_fi_captain/medium/ja_JP-hi_fi_captain-medium.onnx
curl -L -o ja_JP-hi_fi_captain-medium.onnx.json \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/ja/ja_JP/hi_fi_captain/medium/ja_JP-hi_fi_captain-medium.onnx.json

# 4. ナレーション5文を個別に合成(results.md 4節の表のテキストを使用)
source .venv/bin/activate
piper -m ja_JP-hi_fi_captain-medium.onnx -c ja_JP-hi_fi_captain-medium.onnx.json \
  --sentence-silence 0.3 -f s1.wav <<< "GitHubトレンディング一位のOpenMontageを、有料APIキーなしで実際に動かしてみました。"
# ...s2〜s5も同様(本リポジトリの output/narration_script.txt に全文を収録)

# 5. 5本を結合して1本のナレーション音声にする
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy narration_ja.wav
# このリポジトリの output/narration/narration_ja.wav と同一の生成物になる

# 6. Explainerコンポジション用のpropsをこのリポジトリの day-009-props.json からコピーし、
#    remotion-composer/public/demo-props/day-009.json に配置。
#    音声ファイルも remotion-composer/public/day-009/narration_ja.wav に配置。
cp <このリポジトリ>/experiments/day-009/day-009-props.json \
   OpenMontage/remotion-composer/public/demo-props/day-009.json
cp <このリポジトリ>/experiments/day-009/output/narration/narration_ja.wav \
   OpenMontage/remotion-composer/public/day-009/narration_ja.wav

# 7. レンダリング
cd OpenMontage/remotion-composer
npx remotion render src/index.tsx Explainer day-009.mp4 \
  --props public/demo-props/day-009.json --codec h264 --scale 0.5 \
  --browser-executable="$BROWSER" --ignore-certificate-errors
```

## 中身

- `day-009-props.json`: Remotionの`Explainer`コンポジションに渡したcuts/audio定義
  (5カット、`hero_title` → `stat_card` → `bar_chart` → `stat_card` → `text_card`)。
- `output/day-009.mp4`: 実際にレンダリングした最終動画(960x540, h264+aac, 41.9秒, 3.3MB)。
- `output/narration/narration_ja.wav`: Piper TTS(`ja_JP-hi_fi_captain-medium`)で合成した
  日本語ナレーション(5文を結合、40.3秒)。
- `output/narration_script.txt`: ナレーションの全文(1行1文、`results.md`の表と同一)。
- `results.md`: 実行ログ・つまずき・実測値の正直な記録。

## 依存関係

OpenMontage本体(別途clone、AGPLv3) / Python 3.10+ / Node.js 18+ / FFmpeg /
`piper-tts`(pip) / `pyopenjtalk`(pip、日本語ナレーション用) / Remotion CLI(npm、
OpenMontageの`remotion-composer/`に含まれる)。有料APIキーは一切不要。
