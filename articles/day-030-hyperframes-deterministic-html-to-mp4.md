---
title: "HTML/CSS/GSAPを確定的にMP4動画へ変換するhyperframesを実際に検証した"
emoji: "🎬"
type: "tech"
topics: ["ai", "video", "gsap", "cli", "oss"]
published: false
---

HeyGen社が2026年4月にOSS公開した[hyperframes](https://github.com/heygen-com/hyperframes)(Apache-2.0)を実際にインストールし、自作のGSAPアニメーションをMP4へレンダリングし、同じコマンドを複数回実行して出力が本当に決定的(毎回同じ)かどうかをSHA256で確認した。

## hyperframesとは何か

hyperframesは、HTML・CSS・GSAP/Lottie/Three.jsなどで書いたアニメーションを、ヘッドレスChromeで1フレームずつ確定的にシークしながらスクリーンショットを取り、FFmpegでエンコードすることでMP4動画に変換するフレームワークである。
「HTMLを書くだけで動画になる」ことと、AIコーディングエージェント(Claude Code・Cursor・Codexなど)との連携を前面に押し出しているのが特徴で、CLI・エージェント向けスキル・ブラウザ上のスタジオエディタを備える。
依存パッケージには`puppeteer-core`や`@puppeteer/browsers`が含まれており、内部的にはPuppeteerでヘッドレスChrome(Chrome Headless Shell)を操作している。
コアのHTML→MP4レンダリングに外部APIキーは不要で、GPUも不要である。

## 検証環境と準備

Node.js v22.22.0・ffmpeg 6.1.1という条件で、`npx hyperframes@0.8.209 doctor`を実行すると、Node/ffmpeg/ffprobeはOKだが肝心のChrome Headless Shellが未取得と表示された。

```bash
$ npx hyperframes@0.8.209 browser ensure
```

```
Downloading Chrome Headless Shell v152.0.7977.30 — 100% (113.9 MB / 113.9 MB)
Download complete
   Source:  download
   Path:    /root/.cache/hyperframes/chrome/chrome-headless-shell/linux-152.0.7977.30/...
—  Ready to render.
```

約114MBのダウンロードは問題なく完了し、`doctor`の結果もすべて✓になった。
続けて`npx hyperframes@0.8.209 init demo --example blank --non-interactive --skip-skills`でプロジェクトを雛形から作成した。

## つまずいた点: デフォルトテンプレートのCDN読み込みが失敗した

雛形の`index.html`は`<script src="https://cdn.jsdelivr.net/npm/gsap@.../dist/gsap.min.js">`のようにGSAPをCDNから読み込む構成になっている。
筆者が自作のGSAPアニメーション(後述)に書き換えて`npx hyperframes@0.8.209 check`を実行したところ、次のエラーでランタイムチェックが失敗した。

```
Runtime
  ✗ request_failed: Failed to load npm/gsap@.../dist/gsap.min.js: net::ERR_TUNNEL_CONNECTION_FAILED
  ✗ page_error: Cannot read properties of undefined (reading 'timeline')
```

`npx`や`npm`自体はnpmレジストリやGoogleのChrome配布サーバーに問題なく到達できていたため、ネットワーク全体が止まっていたわけではない。
ヘッドレスChromeのサブプロセスがjsdelivrへのCONNECTトンネルを張れなかったことが原因とみられ、プロキシ環境やサンドボックス化されたCI環境では同様の失敗が起こりうる構成だと分かった。
対処として、`npm pack gsap@3.14.2`でGSAP本体を取得し、プロジェクト内の`vendor/gsap.min.js`として同梱、`<script src="vendor/gsap.min.js">`に変更して外部CDNへの依存を排除した。
この修正後は`npx hyperframes@0.8.209 check`が0エラーで通過した(警告2件は「最初のフレームが背景のみ」「字幕の表示時間がやや短い」という演出上の指摘で、レンダリング自体には影響しない)。
hyperframes自身のドキュメントにも「Only deterministic logic — no network fetches」という注意書きがあり、レンダリング時に外部ネットワークへ依存しない構成はツールが推奨する方向とも一致していた。

## 自作したアニメーション

1920x1080・30fps・6秒のコンポジションを、GSAPのタイムラインで以下の3シーンとして組んだ。

- 0.0〜1.6秒: タイトルがぼかし+フェードインで登場
- 1.4〜4.2秒: 3本の棒グラフがそれぞれ異なる幅・タイミングで`power2.out`イージングにより伸びる
- 4.0〜6.0秒: 数値が0から300まで`onUpdate`コールバックでテキストとしてカウントアップ

`npx hyperframes@0.8.209 snapshot --at 0.3,2.4,5.0`で各シーンを静止画確認し、意図通りに表示されていることを目視で確かめた。

![3シーンのコンタクトシート](https://raw.githubusercontent.com/Matsushima-A-830/ai-100days/main/experiments/day-030/snapshots/contact-sheet.jpg)

## レンダリングと決定性の検証

```bash
$ npx hyperframes@0.8.209 render -o renders/run1.mp4
```

```
◇  renders/run1.mp4
   270.8 KB · 6.0s video · rendered in 13.3s
   beginframe capture · software gpu · ... capture 11.1s · encode (during capture) 11.1s
```

出力は1920x1080・H.264(High profile)・30fps・180フレーム・6.000秒・277,342バイトのMP4になった。
本記事の核心として、同じコマンドをさらに2回実行し(`run2.mp4`、`run3.mp4`)、SHA256ハッシュを比較した。

```bash
$ sha256sum run1.mp4 run2.mp4 run3.mp4
3af0d4fdf2db52e98fa4056b8d683149031d7981554c5817e393ad2c4d21d06e  run1.mp4
3af0d4fdf2db52e98fa4056b8d683149031d7981554c5817e393ad2c4d21d06e  run2.mp4
3af0d4fdf2db52e98fa4056b8d683149031d7981554c5817e393ad2c4d21d06e  run3.mp4
```

3回ともバイト単位で完全に一致した。
このレンダリングはデフォルトで2ワーカーによる並列フレームキャプチャを使っているが、並列化によってフレーム順序やタイムスタンプが揺れるような非決定性は見られなかった。
「同じHTML+CSSから毎回同じMP4が出る」という、hyperframesが謳う核心的な主張を、実際に3回レンダリングしてハッシュを突き合わせることで確認できた。

## まとめ

- `npx hyperframes browser ensure`によるChrome Headless Shellの自動取得、`doctor`/`check`/`snapshot`/`render`という一通りのCLIコマンドは、いずれも実際に動作した。
- デフォルトテンプレートが外部CDNからGSAPを読み込む構成になっており、プロキシ環境ではヘッドレスChromeからのCDNアクセスが失敗しうる。ライブラリをプロジェクトに同梱してローカル参照に切り替えることで回避できた。
- 同じコンポジションを3回レンダリングした結果、出力MP4はSHA256が完全一致するバイト単位の決定性を持つことを確認した。
- コアのHTML→MP4レンダリングに追加の有料APIキーは不要だった。

## 出典・ライセンス

- リポジトリ: https://github.com/heygen-com/hyperframes (Apache-2.0)
- npmパッケージ: https://www.npmjs.com/package/hyperframes
- 検証コード・実行ログ・レンダリング済みMP4の全文は[GitHubリポジトリのexperiments/day-030](https://github.com/Matsushima-A-830/ai-100days/tree/main/experiments/day-030)を参照。
