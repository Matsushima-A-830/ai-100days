---
title: "指示文だけでMermaidを卒業できるか? diagram-designスキルを手を動かして検証した"
emoji: "🖼️"
type: "tech"
topics: ["ai", "claudecode", "svg", "agentskill", "diagramming"]
published: false
---

## 今日のネタ: diagram-design

GitHub Trendingで急伸していた [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) というリポジトリを検証した。
自然言語の指示だけで、自己完結したHTML+インラインSVGのエディトリアル調図解を生成するClaude Code向けのagent skillである。
ライセンスはMIT(Copyright (c) 2025 Cathryn Lavery)で、検証時点のHEADは `f4547ee` だった。
筆者が検索した範囲ではZenn・Qiita・noteのいずれにも日本語での一次紹介記事は見つからなかった(2026-10-08時点)。

## 検証方針が崩れた話

本来は公式の手順どおり、Claude Codeにこのリポジトリをplugin marketplaceとして追加して試すつもりだった。

```
/plugin marketplace add cathrynlavery/diagram-design
/plugin install diagram-design@diagram-design
```

ところが、今回使っているクラウド実行環境では、この `plugin marketplace add` コマンドがサンドボックスの自動パーミッション分類器によって拒否された。
理由は `Untrusted Code Integration` だった。
念のためリポジトリをread-onlyでcloneし、同梱のPythonスクリプト(`self_check.py` や `verify-geometry.py` など、チェックリストに「動かして確認せよ」と書かれているスクリプト)を直接実行してみたが、こちらも `Code from External` という理由で拒否された。
どちらも環境側の安全策であり、回避を試みるのは筋が違うと判断し、素直に別の検証方法に切り替えた。

## 方針転換: スキルの指示書を自分の手で忠実に適用する

このスキルの正体は、実行可能なプログラムではなく `SKILL.md` という非常に具体的な指示書(Markdown)と、図のタイプ別リファレンス、そして検証済みのサンプルHTMLの集合である。
つまり「エージェントがこの指示書を読んで従う」ことそのものがスキルの動作原理であり、plugin機構を経由しなくても、指示書を自分で読んで同じように手を動かせば、スキルが本来やろうとしていることの価値は検証できるはずだと考えた。

具体的には次の手順を踏んだ。

1. `skills/diagram-design/SKILL.md` と、スイムレーン図のタイプ別リファレンス `references/type-swimlane.md` を読む。
2. 同梱サンプル `assets/example-swimlane.html` の、既に検証済みの座標・矢印ルーティングをそのまま流用する。
3. テキスト内容だけを、このai-100daysリポジトリ自身の1日の運用フロー(`CLAUDE.md` に書かれている「朝: リサーチRoutine → 通勤中: 人間がマージ → 昼: 実装Routine → 夜: 人間がレビュー・公開」)に差し替える。
4. 比較用に、同じ内容を実際のMermaid.js(v11.4.1)でもレンダリングする。
5. 両方を実際にブラウザ(環境にプリインストールされたChromium、Playwright経由)で開き、崩れがないか・コンソールエラーが出ていないかを確認する。

## 実際に作った図

4レーン(RESEARCH / COMMUTE / IMPL / EVENING)・7ノード・6矢印の構成で、Routineが自動で動く部分と人間が判断する部分の境界、そして「today.mdが未設定なら何もしない」という条件分岐を破線の矢印で表現した。

比較対象として、同じ内容を素のMermaidでも描いた。
最初はCDN(`cdn.jsdelivr.net`)からmermaid.min.jsを読み込む形で書いたが、この実行環境のネットワークポリシーでCDNへの接続が拒否され、ブラウザのコンソールに次のエラーが出た。

```
console: Failed to load resource: net::ERR_TUNNEL_CONNECTION_FAILED
pageerror: mermaid is not defined
```

`registry.npmjs.org` は直結が許可されていたため、`npm pack mermaid@11.4.1` でパッケージを取得し、ローカルのmermaid.min.js(2,571,900バイト)を参照する形に差し替えたところ、コンソールエラーなしで描画できた。

diagram-design版は最初から外部リソースがGoogle Fontsのみで、コンソールエラー・ページエラーともになく一発で描画できた。

見た目の差は次の画像の通りで、Mermaid版はSKILL.mdが名指しで批判している「Reproducing Mermaid's renderer layout」そのものの、サブグラフが薄黄色・全ノード同色という見た目になった。
diagram-design版は、ドット地紋の背景・レーンラベル・Instrument Serifの見出し・1〜2箇所だけのコーラルアクセント(クリティカルな人間レビューの手渡しと最終成果物のノード)という、一貫した編集デザインになった。

実際のスクリーンショットは `experiments/day-011/before-mermaid.png`(素のMermaid版)と `experiments/day-011/after-diagram-design.png`(diagram-design版)としてリポジトリに置いてあるので、興味があれば見比べてほしい。

## 自動チェックの代わりに手でチェックリストを当てた

`self_check.py` が実行できなかったため、SKILL.md §9の「Pre-Output Checklist」を1項目ずつ目視・座標計算で確認した。
アクセシビリティ属性(`role="img"`、`aria-labelledby`、`<title>`が`<defs>`より前)、矢印とラベルマスクの重なり、コーラルの使用数が2要素以内であること、複雑度予算(最大9ノード・12矢印)の範囲内であることなどを確認し、すべて満たしていた。

ただし1点だけ、同梱サンプルの `example-swimlane.html` 自体が、チェックリストにある「SVGを `overflow-x: auto` のラッパーで囲む」という要件を満たしていないことに気づいた。
手動適用した自分の版ではこの点を追加で満たすようにした。
スキルの指示書と同梱サンプルの間に小さな不整合があるという発見である。

## わかったこと

このスキルの価値は、Pythonスクリプトを実行することではなく、SKILL.md自体が色トークン・間隔のグリッド・矢印のマスク規則・複雑度の予算・44種類の図のタイプ別リファレンスという、非常に具体的で再現性のある設計ルール集になっている点にあるとわかった。
plugin機構もコード実行もできない制約下でも、指示書を読んで手で忠実に適用するだけで、素のMermaidとは明確に違う見た目の図を一回で作れた。
これは「指示文だけで図解を自動生成する」という触れ込みの核心を支持する結果だと筆者は考える。

一方で、今回は公式のplugin経由のインストール・起動そのものは検証できておらず、オンボーディング時のスタイルガイド対話(SKILL.md §0で説明されている、初回利用時に配色をカスタマイズするか聞かれるフロー)や自動チェックスクリプトの実行結果は未確認のままである。
この制約は検証の限界として正直に書いておく。

## 参考

- リポジトリ: https://github.com/cathrynlavery/diagram-design
- 検証コード・実行ログ: `experiments/day-011/`
