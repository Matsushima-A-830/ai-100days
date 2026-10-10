---
title: "GitHubトレンドの動画生成agent skill「video-shotcraft」を実際にレンダリングしてみた"
emoji: "📼"
type: "tech"
topics: ["ai", "oss", "remotion", "agentskill", "video"]
published: false
---

筆者は海外のAI関連ニュースを毎日1本検証して発信するチャレンジの12日目として、[video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)というOSSを動かしてみた。Claude Code/Codex向けのagent skillとして、Remotion(Reactベースの動画生成フレームワーク)を土台に「映画的なプロダクト動画」を自動生成する。157枚のショットレシピカード・214本のモーションプレビューを備え、すぐ使える36.2秒のプロモ用テンプレート「Ink Press」が同梱されている。ライセンスはApache-2.0。検証したcommitは`5ddbf52`(著者日時2026-09-29)。筆者が検索した範囲ではZenn・Qiita・noteのいずれにも日本語での一次紹介記事は見つからなかった(2026-10-09時点)。

結論から書く。**追加の有料APIキー・GPUなしで、公式スペック通り「36.2秒・1920×1080・30fps・10ショット」のプロモ動画を実際にレンダリングできた。** 9日目に検証した[OpenMontage](https://github.com/calesthio/OpenMontage)でも同じRemotionベースの動画生成OSSを扱ったので、今回はその時に遭遇したheadlessレンダリングの詰まりどころが再現するかを比較軸にした。結果は、9日目に必須だった外部フォントのTLS証明書エラー対策が今回は不要で、その理由はコンポジション側の設計にあった、というものだった。

## video-shotcraftとは何か

公式README(日本語版も同梱されている)によれば、本体は157枚の「ショットレシピカード」(目的・エネルギー・推奨時間・パラメータ・実装上の注意点をまとめたMarkdown)と214本のモーションプレビューのライブラリで、Claude CodeやCodexにagent skillとして追加すると、自然言語の指示から該当するショットを組み合わせてRemotionコンポーネントを生成する。単体のショット合成に加えて、あらかじめ検証済みの完全な36.2秒プロモ動画テンプレート「Ink Press」が同梱されており、READMEは「これが最も速く確実に高品質な動画に辿り着く道」と位置付けている。今回はこの「Ink Press」をそのままレンダリングする検証を行った。

## 実測1: day-009で必須だった外部フォントのTLSエラー対策は、今回は不要だった

video-shotcraftのREADMEは「Headless / CI notes」として、低スペックなLinux環境でのレンダリング時に遭遇する壁を事前に明記している。そのうち、day-009(OpenMontage)の検証で実際に扱った2つについて、今回どうなったかを比較した。

| 壁 | day-009(OpenMontage) | day-012(video-shotcraft) |
|---|---|---|
| 低コア機での`--concurrency`上限エラー | 遭遇せず | 遭遇せず(4コア環境で`--concurrency=1`指定のみで解決) |
| 外部フォント読み込み時のTLS証明書エラー(`ERR_CERT_AUTHORITY_INVALID`) | 遭遇(`--ignore-certificate-errors`が必須だった) | **遭遇せず** |

外部フォントのエラーが今回だけ起きなかった理由をソースコードで確認したところ、偶然ではなく設計の違いだった。OpenMontageのコンポジションは外部フォントサービスから都度フォントを取得していたのに対し、video-shotcraftの`template/src/`配下は`SERIF` / `SANS` / `MONO`という定数しか使っておらず(`grep -rn fontFamily template/src`で確認)、その中身は`ui-serif, Georgia, "Times New Roman", serif`のようなシステムフォントのフォールバックスタックだった。`@font-face`やGoogle Fontsの読み込みは0件で、レンダリング時にフォントのために外部ネットワークへアクセスしない。**同じRemotion・同じheadless実行環境でも、動画側の実装が外部リソースに依存するかどうかで詰まりどころが変わる**、というのは実際に2つのリポジトリを手で動かして比較しないと得られない知見だった。

## 実測2: フル解像度でもscale=0.5でも、実際に最後までレンダリングできた

```
$ npx remotion render src/index.ts AiflPromo out/promo.mp4 \
    --concurrency=1 --scale=0.5 --codec=h264
Rendered 1085/1085
Encoded 1085/1085
+                    out/promo.mp4 8.4 MB

real	1m35.815s
```

(コマンドは、実行環境ごとに異なるブラウザの場所の指定を省いて表記している。)

`ffprobe`で検証すると、`h264 960x540` + `aac`、`duration=36.224000`秒。README/TEMPLATE.mdが謳う「36.2秒」という尺に実測値がぴったり一致した。さらに公式スペック通りのフル解像度(1920×1080、`--scale`指定なし)でも実際にレンダリングした。

```
$ time npx remotion render src/index.ts AiflPromo out/promo-1080p.mp4 \
    --concurrency=1 --codec=h264
Rendered 1085/1085
Encoded 1085/1085
+                    out/promo-1080p.mp4 20.3 MB

real	3m28.997s
```

こちらも`h264 1920x1080` + `aac`、`duration=36.224000`秒とscale=0.5版と尺が一致した。レンダリング実時間はscale=0.5版(1m35s)の約2.2倍で済み、ピクセル数が4倍になった割には緩やかな増加だった。リポジトリにはサイズの都合でscale=0.5版(8.4MB)のみをコミットし、フル解像度版(20.3MB)は実測値のみこの記事とresults.mdに残している。

テンプレート自身が推奨する手順どおり、本番レンダリングの前にまず1フレームだけ静止画として書き出して画質を確認した(`npx remotion still ... --frame=150`)。出力は1920×1080・1.2MBのPNGで、英語・中国語混在のダミーUIのテキスト、カードの影、2.5Dの傾き演出とも崩れなく確認できた。TEMPLATE.mdが警告する「`transform: scale`だと文字が先にダウンサンプリングされて滲む」問題は、少なくともこのフレームの範囲では視認できなかった。

## 実測3: 紹介文の数値と実測値は食い違ったが、原因は「スナップショットが古かった」ことだった

backlog.mdに記録した紹介文の数値(2026-10-09時点のGitHub Trending掲載情報)は「152枚のショットレシピカード・209本のモーションプレビュー」だったが、実際にcloneしたcommit(`5ddbf52`、著者日時2026-09-29)では数値が異なっていた。

| 項目 | backlog.mdの紹介文 | 実測値 |
|---|---|---|
| ショットレシピカード | 152 | **157** |
| モーションプレビュー | 209 | **214** |

ただし、day-009のケースと違ってこれは紹介文自体の誤りではなかった。README.mdを読むと、「152カード/209プレビュー」は2026-08時点の拡張履歴として明記された**過去のマイルストーン**の数値であり、現在のREADMEが掲げている数値は「157カード・214プレビュー」だった。その上で、この「現在の数値」が実態と一致するかを裏取りした。

```
$ find references/shots -name "*.md" | wc -l   # ATTRIBUTION.md(ライセンス記録)1件を含む
158
$ python3 -c "import json; d=json.load(open('gallery/api/library.json')); print(d['stats'])"
{'cardCount': 157, 'styleCount': 214, 'previewCount': 214, 'mediaCount': 214}
```

`references/shots/`配下のMarkdown158件から、ショットレシピカードではない`ATTRIBUTION.md`を1件除くと157件になり、Gallery自身が生成する統計(`library.json`)とも完全に一致した。day-009ではツール数・skill数で紹介文と実測が大きく食い違っていたが、今回食い違っていたのは「backlog.mdが参照した時点のスナップショット」と「検証時点のリポジトリの状態」であり、数日の間にリポジトリが更新され続けていたことによる自然なズレだった。日々活発に更新されているリポジトリを数日越しに検証する際は、紹介文の数値をそのまま転記せず、検証時点で改めて裏取りする価値があると今回も確認できた。

## 実測4: 同梱のユニットテストも実際に動かした

video-shotcraftリポジトリ直下には、`assets/lib/helpers`配下の純粋関数に対するvitestのユニットテストが同梱されている。これも実際に動かした。

```
$ npm install && npx vitest run
 ✓ assets/lib/helpers/__tests__/helpers.test.ts (23 tests) 89ms
 Test Files  1 passed (1)
      Tests  23 passed (23)
```

23件すべてパスした。

## 実測5: 別環境(Windows)でも再現し、見た目の差も分かった

自動実行の記録を鵜呑みにしないため、筆者の手元(Windows 11・Node v24.15.0・16論理コア)で同じcommit `5ddbf52`をcloneして再現した。

```
$ npx remotion render src/index.ts AiflPromo out/promo.mp4 --concurrency=1 --scale=0.5 --codec=h264
Rendered 1085/1085
Encoded 1085/1085
+                    out/promo.mp4 8.5 MB
(所要 約1m07s)
```

`ffprobe`では`h264 960x540` + `aac`、`Duration: 00:00:36.22`で、自動実行時の36.224秒と一致した。157カード・214プレビューの数値とvitestの23件パスも同じだった。一方で、見た目には環境差があった。同じframe=150でも、見出し "One card," の幅が環境で変わった(右端がLinux版で約540px、Windows版で約615px)。`ui-serif, Georgia, ...`というスタックがOSごとに別のフォントに解決されるためで、ファイルサイズも8,415,916 bytes(Linux)と8,549,911 bytes(Windows)で一致しない。尺とフレーム数は同じでも、見た目まで環境非依存とは言えない。外部フォントを使わないことは、詰まりにくさと引き換えに、環境ごとにタイポグラフィが変わるという性質も持つ。

フル解像度版の再レンダリングは手元ではしていない。

## ライセンスについて

- video-shotcraft本体: Apache-2.0(`LICENSE`ファイルで確認)。
- レンダリングに使うRemotion本体: Remotion独自のCompany License。個人・従業員3名以下の営利企業・非営利団体は無料で利用可能(商用含む)だが、4名以上の営利企業は有料のCompany Licenseが必要([remotion.dev/docs/license/terms](https://remotion.dev/docs/license/terms))。Remotion 5.0で条件が変更される可能性があるとの情報もあったため、実際に商用利用する場合は都度最新の条件を確認したほうがよい。
- SFX素材: Mixkit Sound Effects Free License。リポジトリ同梱の`assets/audio/ATTRIBUTION.md`に逐ファイルの出典URLが記録されている一方、一部の古い音源は原URLが反査できず「商用前に要確認」とリポジトリ自身が明記していた。

## まとめ

GitHub Trendingで話題になっていたvideo-shotcraftを、有料APIキー・GPUなしで実際にレンダリングし、同梱のテンプレート「Ink Press」が公式スペック通りの36.2秒・10ショットの動画として出力されることを確認できた。day-009(OpenMontage)との比較では、9日目に必須だった「外部フォントのTLS証明書エラー」対策が、今回はコンポジションが外部リソースに依存しない設計だったため不要だった。同じRemotion・同じheadless環境でも、動画側の実装次第で詰まりどころが変わることを、2つのOSSを手を動かして比較することで確認できた。

- 出典: https://github.com/Vincentwei1021/video-shotcraft (Apache-2.0)
- 検証commit: `5ddbf521038b0a7accfb6dc1e0a9eb29c67277ab`
- 比較対象(day-009): https://github.com/calesthio/OpenMontage (AGPLv3)
