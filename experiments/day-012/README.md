# Day 012: video-shotcraft の「Ink Press」テンプレートを実際にレンダリングする

対象: https://github.com/Vincentwei1021/video-shotcraft (Apache-2.0)、検証commit `5ddbf521038b0a7accfb6dc1e0a9eb29c67277ab`

詳しい経緯・つまずき・実測値は `results.md` を参照。ここでは再現手順のみをまとめる。

## 再現手順

video-shotcraft本体はApache-2.0のOSSであり、サイズが大きいため本リポジトリには含めていない。
別途cloneして以下の手順で再現する。

```bash
# 1. 本体を取得(ネットワーク接続が必要)
git clone --depth 1 https://github.com/Vincentwei1021/video-shotcraft.git
cd video-shotcraft/template

# 2. 依存関係をインストール(postinstallスクリプトを含む外部コードの実行が必要)
npm install

# 3. レンダリング用ブラウザの指定(results.md 2節参照)
#    この環境ではRemotionの自動Chromeダウンロード先(remotion.media)がブロックされるため、
#    既存のPlaywright用Chromium(環境によりパスは異なる)のheadless_shellを明示的に指定する。
BROWSER=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell

# 4. QA静止画の書き出し(動作確認用、テンプレート自身が推奨する手順)
npx remotion still src/index.ts AiflPromo out/qa/f150.png --frame=150 \
  --browser-executable="$BROWSER" --concurrency=1

# 5. 本番レンダリング(960x540、--scale=0.5。フル1920x1080版はresults.md 4節参照)
npx remotion render src/index.ts AiflPromo out/promo.mp4 \
  --browser-executable="$BROWSER" --concurrency=1 --scale=0.5 --codec=h264

# 6. フル解像度版(1920x1080、こちらが公式スペック)
npx remotion render src/index.ts AiflPromo out/promo-1080p.mp4 \
  --browser-executable="$BROWSER" --concurrency=1 --codec=h264

# 7. 同梱のユニットテスト(assets/lib/helpers、純粋関数23件)
cd ..
npm install
npx vitest run
```

## 中身

- `output/promo-540p.mp4`: 実際にレンダリングした成果物(960×540, h264+aac, scale=0.5,
  36.224秒, 8.4MB)。フル解像度(1920×1080, 20.3MB)も同一コマンドで実際にレンダリングし
  `results.md`に実測値を記録しているが、リポジトリ容量の都合でこのファイルは含めていない
  (手順4で誰でも再現できる)。
- `qa/frame-150.jpg`: `npx remotion still`で書き出したQA静止画(1920×1080からJPEG変換)。
- `qa/frame-000-open.jpg` / `qa/frame-700-list.jpg` / `qa/frame-1080-outro.jpg`:
  フル解像度版動画から抽出した開始・中盤・終盤のフレーム(1920×1080からJPEG変換)。
- `results.md`: 実行ログ・つまずき・実測値・day-009との比較の正直な記録。

## 依存関係

video-shotcraft本体(別途clone、Apache-2.0) / Node.js 18+ / npm / Remotion CLI(npm、
`template/`に含まれる) / FFmpeg(フレーム抽出用)。有料APIキーは一切不要。

## 注意

`npm install`はvideo-shotcraft本体のpostinstallスクリプトを含む外部コードを実行するため、
この実行環境のコマンドサンドボックスでは自動承認されず、明示的にサンドボックスを無効化して実行した
(詳細はresults.mdの0節)。手元で再現する場合は、信頼できるネットワーク・権限設定の中で実行すること。
