# Day 030 — hyperframes: HTML/CSS/GSAPを確定的にMP4へレンダリングする

対象: https://github.com/heygen-com/hyperframes (Apache-2.0, npmパッケージ `hyperframes`)

## 再現手順

前提: Node.js 22以上、ffmpeg(PATHに存在すること)。外部APIキーは不要。

```bash
# 1. 依存チェック(Chrome Headless Shellが無ければ案内が出る)
npx hyperframes@0.8.209 doctor

# 2. Chrome Headless Shellを取得(数百MBのダウンロードが発生する)
npx hyperframes@0.8.209 browser ensure

# 3. プロジェクト雛形を作成
npx hyperframes@0.8.209 init demo --example blank --non-interactive --skip-skills
```

`demo/index.html` を本リポジトリ同梱のものに差し替える(このディレクトリの `demo/index.html` がそれ)。
GSAP本体はCDNではなく `demo/vendor/gsap.min.js` を同梱して読み込んでいる(理由はresults.md参照)。

```bash
cd demo

# 4. Lint/ランタイム/レイアウト/コントラストを一括チェック
npx hyperframes@0.8.209 check

# 5. 静止画で目視確認(任意)
npx hyperframes@0.8.209 snapshot --at 0.3,2.4,5.0 -o ../snapshots --no-end

# 6. MP4へレンダリング
npx hyperframes@0.8.209 render -o ../renders/run1.mp4

# 7. 決定性の確認: 同じコマンドをもう一度実行し、SHA256を比較する
npx hyperframes@0.8.209 render -o ../renders/run2.mp4
sha256sum ../renders/run1.mp4 ../renders/run2.mp4
```

## このディレクトリの内容

- `demo/` — hyperframesのプロジェクト一式(`index.html`が本体、`vendor/gsap.min.js`はCDN代替として同梱、`CLAUDE.md`/`AGENTS.md`/`hyperframes.json`/`meta.json`/`package.json`は`hyperframes init`が自動生成したもの)
- `renders/run1.mp4` — レンダリング結果のMP4(1920x1080, 30fps, 6秒)
- `snapshots/` — レンダリング前に目視確認した静止画(`contact-sheet.jpg`が3シーンのコンタクトシート)
- `results.md` — 検証の詳細・CDN読み込み失敗とその回避・決定性検証のSHA256記録
