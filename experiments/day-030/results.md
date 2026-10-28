# Day 030 — hyperframes (heygen-com/hyperframes) 検証結果

- 出典: https://github.com/heygen-com/hyperframes
- 検証日: 2026-10-28
- 検証対象: hyperframes CLI v0.8.209 (npm経由で`npx hyperframes@0.8.209`として実行。ライセンス: Apache-2.0)
- 検証環境: Node.js v22.22.0 / ffmpeg 6.1.1-3ubuntu5 / Routineのクラウド実行環境(Chromiumはこのセッション向けに事前インストールされていたプリビルド版ではなく、hyperframes自身が`npx hyperframes browser ensure`でダウンロードしたChrome Headless Shell v152.0.7977.30を使用)

## やったこと

1. `npm view hyperframes` でパッケージ情報を確認(deps: puppeteer-core, @puppeteer/browsers等)。
2. `npx hyperframes doctor` でシステム依存関係をチェック。Node/ffmpeg/ffprobeはOKだったが、Chrome Headless Shellは未取得と表示された。
3. `npx hyperframes browser ensure` を実行したところ、Chrome Headless Shell v152.0.7977.30 (113.9MB) のダウンロードに成功した(このRoutine実行環境のネットワークプロキシ経由でGoogleのChrome配布サーバーに到達できた)。
4. `npx hyperframes init demo --example blank --non-interactive --skip-skills` でプロジェクトを雛形から作成。
5. `demo/index.html` を自作のGSAPアニメーションに書き換えた。内容は以下の3シーン、合計6秒・1920x1080・30fps:
   - 0.0〜1.6秒: タイトルがぼかし+フェードインで登場
   - 1.4〜4.2秒: 3本のバーチャート(棒グラフ)がそれぞれ異なる幅・タイミングでpower2.outイージングにより伸びる
   - 4.0〜6.0秒: `gsap`のtweenプロキシでテキストの数値を0→300まで非DOM直結のカウントアップ(`onUpdate`でテキストを書き換え)
6. `npx hyperframes check` を実行したところ、テンプレートに書かれていたGSAPのCDN読み込み(`cdn.jsdelivr.net`)が `net::ERR_TUNNEL_CONNECTION_FAILED` で失敗しレンダリングエラーになった。これはヘッドレスブラウザのプロセスが素のネットワークプロキシ設定を引き継がずjsdelivrへのCONNECTトンネルを張れなかったことが原因と考えられる(`npx`/`npm`のCLIプロセス自体はプロキシ経由でnpmレジストリやGoogleのChrome配布サーバーに到達できていたため、プロキシ自体の問題ではなくChromeサブプロセスの設定差によるものと判断した)。
   - **対処**: `npm pack gsap@3.14.2`でGSAP本体を取得し、`demo/vendor/gsap.min.js`としてプロジェクトに同梱、`<script src="vendor/gsap.min.js">`へ変更。これにより外部CDNへの依存を排除した。hyperframes自身のドキュメント(`demo/CLAUDE.md`)にも「Only deterministic logic — no network fetches」という注意書きがあり、レンダリング時に外部ネットワークに依存しないことはそもそもツールの推奨構成とも一致する。
   - この修正後は`npx hyperframes check`が通過(0 error, 2 warning。警告は「最初のフレームが背景だけ」「字幕表示時間がやや短い」という演出上のcraft指摘であり、レンダリング自体を妨げるものではない)。
7. `npx hyperframes snapshot --at 0.3,2.4,5.0` で静止画を確認(`snapshots/contact-sheet.jpg`)。意図した3シーンが正しく表示されていることを目視確認した。
8. `npx hyperframes render -o ../renders/run1.mp4` でMP4へレンダリング。成功。
   - 出力: 1920x1080, H.264 (High profile), 30fps, 180フレーム, 6.000秒, 277,342 bytes, bit_rate 369,789 bps
   - レンダリング時間: 13.3秒(`real 0m16.467s`。2 workerで並列キャプチャ)
9. **決定性(再現性)の検証**: 同じ`npx hyperframes render`コマンドを合計3回実行し(`run1.mp4`, `run2.mp4`, `run3.mp4`)、`sha256sum`で比較した。

```
$ sha256sum run1.mp4 run2.mp4 run3.mp4
3af0d4fdf2db52e98fa4056b8d683149031d7981554c5817e393ad2c4d21d06e  run1.mp4
3af0d4fdf2db52e98fa4056b8d683149031d7981554c5817e393ad2c4d21d06e  run2.mp4
3af0d4fdf2db52e98fa4056b8d683149031d7981554c5817e393ad2c4d21d06e  run3.mp4
```

3回とも**バイト単位で完全に一致**した(ファイルサイズも277,342 bytesで同一)。2ワーカーによる並列キャプチャを使っているにもかかわらず、フレーム順序や内容に非決定性は見られなかった。

## 検証結果まとめ

| 項目 | 結果 |
|---|---|
| コアのHTML→MP4レンダリング(APIキー不要) | ✅ 成功 |
| GSAPアニメーション(フェード・バーチャート伸長・カウントアップ)の反映 | ✅ 成功(スナップショットで目視確認) |
| 同一入力からの出力の決定性 | ✅ 3回ともSHA256完全一致 |
| `hyperframes doctor` / `check` / `snapshot` / `render` のCLI一通り | ✅ すべて動作 |
| デフォルトテンプレートのCDN読み込み(jsdelivr) | ❌ このRoutine実行環境では失敗(検証に直接関係する失敗として記録。ローカルHTTP配信に切り替えて回避した) |

## 失敗・制約の分類について

- **記事に書く失敗**: デフォルトテンプレートが外部CDN(`cdn.jsdelivr.net`)からGSAPを読み込む構成になっているが、サンドボックス化されたネットワーク環境(社内プロキシ・CI環境など)ではヘッドレスChromeからのCDNアクセスが失敗しうる。これはツールのデフォルト構成(外部CDN依存)に起因する、読者が同様の制限環境で遭遇しうる問題であり、`vendor/`配下にライブラリを同梱してローカル参照に切り替えるという明確な回避策とセットで記事の内容とする。
- **書かない事項**: Chrome Headless Shellのダウンロード自体は今回のRoutine環境のプロキシ経由で成功したため、「ヘッドレスブラウザが入っていない」系の制約には該当しなかった。
