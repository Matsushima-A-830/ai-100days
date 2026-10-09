# Day 011 検証結果: diagram-design (cathrynlavery/diagram-design)

- 出典: https://github.com/cathrynlavery/diagram-design (検証時点のHEAD: `f4547ee95f88e5b28a52517feff6b6c11cc657f9`, 2026-10-08)
- ライセンス: MITライセンス（リポジトリ直下 `LICENSE` ファイルで確認。Copyright (c) 2025 Cathryn Lavery）
- 検証日: 2026-10-09

## やろうとしたこと / 実際にやったこと(正直な記録)

today.md の指示通り、本来は Claude Code にこのリポジトリを公式のplugin marketplaceとして
追加し(`/plugin marketplace add cathrynlavery/diagram-design` →
`/plugin install diagram-design@diagram-design`)、スキルとして動かして検証するつもりだった。

**しかし、この実行環境では以下の2つの操作がサンドボックスの自動パーミッション分類器によって拒否された:**

1. `claude plugin marketplace add cathrynlavery/diagram-design` を実行 →
   `Permission for this action was denied by the Claude Code auto mode classifier.
   Reason: [Untrusted Code Integration]` で拒否。
2. クローンしたリポジトリ内のPythonスクリプト(`scripts/self_check.py`,
   `scripts/verify-geometry.py` など)を直接実行 →
   `Permission for this action was denied ... Reason: [Code from External]` で拒否。

これはクラウド実行環境の安全策であり、回避を試みるのは不適切と判断し、代わりに以下の方法で
検証した(どちらも正直に「公式インストールでの動作確認ではない」ことを明記する):

- リポジトリを読み取り専用で `git clone`(`/tmp/.../scratchpad/day011-src/diagram-design`)し、
  `skills/diagram-design/SKILL.md` と `references/type-swimlane.md`、
  および同梱サンプル `assets/example-swimlane.html` を実際に読んだ。
- このスキルの本体は「Claude Codeに読ませて従わせる指示書(Markdown)」であり、実行可能コードではない。
  そこで**このスキルの指示を自分(Claude)が手で忠実に適用して**、本リポジトリ自身の1日の運用フロー
  (CLAUDE.mdに書かれている「朝Routine→通勤中(人間)→昼Routine→夜(人間)」)を表す
  スイムレーン図を自己完結HTML+インラインSVGとして実際に作った
  (`experiments/day-011/after-diagram-design.html`)。
  これは「指示文だけで狙った見た目の図解を出せるか」というスキルの価値提案そのものを検証している。
- 比較対象として、同じ内容を実際のMermaid.js(v11.4.1)でレンダリングした「素のMermaid」版を
  別ファイルとして作った(`experiments/day-011/before-mermaid.html`)。
- 両方を実際にブラウザ(環境にプリインストールされているChromium、Playwright経由)で開き、
  スクリーンショットを撮って見た目を確認し、コンソールエラー・ページエラーの有無もログに残した。
- 自動チェックスクリプト(`self_check.py` 等)は実行できなかったため、代わりに
  SKILL.md §9 の「Pre-Output Checklist」を自分の目で1項目ずつ確認した(詳細は下記)。

## 実行ログ

### Mermaid版のレンダリング(1回目: CDN直結、失敗)

`before-mermaid.html` は当初 `https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js` を
CDNから読み込む形で書いた。Playwright制御下のChromiumで開いたところ、このクラウド実行環境の
ネットワークポリシーでCDNへの接続が拒否され、描画に失敗した。

```
$ node shot.mjs .../before-mermaid.html .../before-mermaid.png
{"errors":["console: Failed to load resource: net::ERR_TUNNEL_CONNECTION_FAILED","pageerror: mermaid is not defined"]}
```

`curl $HTTPS_PROXY/__agentproxy/status` のログでも確認:

```
{"ts":"...","kind":"connect_rejected","detail":"gateway answered 403 to CONNECT (policy denial or upstream failure)","host":"cdn.jsdelivr.net:443"}
```

### Mermaid版のレンダリング(2回目: npm経由でローカル取得、成功)

`registry.npmjs.org` はこの環境のネットワークポリシーでNO_PROXY(直結許可)に入っていたため、
`npm pack mermaid@11.4.1` でパッケージを取得し、`dist/mermaid.min.js`
(2,571,900 bytes、スクラッチパッド内のみに配置。リポジトリにはコミットしない)を
ローカル参照に差し替えて再実行した。

```
$ npm pack mermaid@11.4.1
npm notice name: mermaid
npm notice version: 11.4.1
npm notice filename: mermaid-11.4.1.tgz
...

$ node shot.mjs .../before-mermaid-local.html .../before-mermaid.png
{"errors":[]}
```

コンソールエラーなし。`before-mermaid.png` を生成(本リポジトリにはこのPNGのみコミットし、
2.5MBのmermaid.min.js自体はコミットしない)。

### diagram-design版のレンダリング

```
$ node shot.mjs .../after-diagram-design.html .../after-diagram-design.png
{"errors":[]}
```

コンソールエラー・ページエラーともになし。外部読み込みはGoogle Fonts(Instrument Serif /
Geist / Geist Mono)のみで、SKILL.md §12 の「Embedded CSS (no external except Google Fonts),
Inline SVG (no external images)」という単一ファイル完結の要件を満たしている。

## 見た目の比較(Before/After)

- Before(素のMermaid, デフォルトテーマ): `before-mermaid.png`
- After(diagram-design skillの指示を手動適用): `after-diagram-design.png`

Mermaid版はサブグラフが薄黄色の背景、ノードが全ノード同一色のラベンダー、フォントもブラウザ
デフォルトのsans-serifで、SKILL.mdが名指しで批判している「Reproducing Mermaid's renderer
layout」そのものの見た目になった。

diagram-design版は、同じ情報量(4レーン・7ノード・6矢印)に対して、ドット地紋の背景、
レーンごとのラベル、Instrument Serifの見出し、Geist Mono のeyebrow/ラベル、
1〜2箇所だけのコーラルアクセント(クリティカルな人間レビューの手渡しと、最終成果物のノード)、
ホバーで情報量過多にならない凡例、という一貫した編集デザインになった。見た目の差は明確。

## SKILL.md §9 Pre-Output Checklistの手動確認(自動スクリプトの代わり)

自動チェックスクリプト(`self_check.py`, `verify-geometry.py`)は実行権限がなく動かせなかったため、
`after-diagram-design.html` を目視・座標計算で1項目ずつ確認した。

- [x] `<svg>` に `role="img"` と `aria-labelledby="day011-swimlane-title day011-swimlane-desc"` がある
- [x] `<title>` が `<defs>` より前、`<svg>` の最初の子要素になっている
- [x] `<title>`/`<desc>` のIDがこの図固有のプレフィックス付き(`day011-swimlane-*`)。裸の `title`/`desc` ではない
- [x] 矢印(`<line>`/`<path>`)がノードのボックスより先(DOM順で上)に書かれている
- [x] 接続線はすべて直交(水平/垂直、または1回だけ曲がる`Q`カーブ)で斜め線なし
- [x] 矢印ラベルはすべて不透明な `<rect>` マスクの上に乗っており、線との間に6px以上の隙間がある
- [x] ラベルマスクと、それより後に描画されるノードボックスが座標上重なっていない(手計算で確認。例: 1本目のラベル `x=528,y=140,w=60,h=12` に対し後続ノード `Merge PR` は `y=176〜224` で非接触)
- [x] コーラル(accent)は2要素のみ(クリティカルハンドオフの矢印1本 + `Publish & sync` ノード1個)
- [x] 凡例は使われている4種類の要素(Step / Focal outcome / Within-lane step / Conditional gate / Critical handoff)を過不足なくカバー
- [x] ノード数7・矢印6で、§7の複雑度予算(最大9ノード・12矢印・コーラル2)の範囲内
- [x] 見出しはInstrument Serif、ノード名はGeist 600、サブラベル/eyebrow/矢印ラベルはGeist Mono。JetBrains Monoは不使用
- [x] SVGを `overflow-x: auto` の `.wrap` 要素でラップし、`min-width` をviewBox幅(900)に合わせてある
  (同梱サンプル `example-swimlane.html` 自体はこのラッパーdivを持っておらず、チェックリスト
  §9の該当項目を厳密には満たしていなかった。手動適用時にこちらで追加して満たした)

## わかったこと・率直な所感

- **プラス**: このスキルの価値は「Pythonスクリプトを実行すること」ではなく、SKILL.md自体が
  非常に具体的で再現性のある設計ルール集(色トークン、間隔のグリッド、矢印のマスク規則、
  複雑度の予算、44種類の図のタイプ別リファレンス)になっている点にある。公式のplugin
  インストールが使えない制約下でも、指示書を読んで手で忠実に適用するだけで、素のMermaidとは
  明確に違う「編集デザイン誌っぽい」見た目の図を一回で作れた。これは「指示文だけで図解を
  自動生成する」という触れ込みの核心を支持する結果。
- **マイナス/注意点**: 同梱サンプル(`example-swimlane.html`)自体がスキル自身のチェックリスト
  (§9の `overflow-x: auto` ラッパー要件)を完全には満たしていなかった。スキルの指示と
  同梱サンプルの間に小さな不整合がある。
- **検証の限界(当初)**: 公式のplugin経由のインストール・起動は今回のクラウド実行環境のサンドボックス
  ポリシーにより確認できなかった。また `scripts/self_check.py` や `scripts/verify-geometry.py`
  による自動検証も実行できず、目視・手計算での代替確認にとどまっていた。
  → **後日(2026-10-09)、人間がローカルPCで公式インストール・`self_check.py`実行の両方を実施し、
  手動適用が自動チェックにも合格すること、および同梱サンプルの不整合は自動チェックの対象外である
  ことを確認した(詳細は上記の追記セクション)。
- PNG書き出し(`scripts/export_svg.py` 経由)もコード実行が必要なため今回は試していない。
  今回はSVGをそのままHTML埋め込みで確認するところまで。

## 追記(2026-10-09、人間のローカルPCで公式インストールを実際に試した結果)

クラウドRoutine環境ではブロックされていた公式インストールを、ローカルPC(サンドボックス外)で
実際に試した。

```
$ claude plugin marketplace add cathrynlavery/diagram-design
✔ Successfully added marketplace: diagram-design (declared in user settings)

$ claude plugin install diagram-design@diagram-design
✔ Successfully installed plugin: diagram-design@diagram-design (scope: user)
```

両方とも問題なく成功した。`claude plugin details diagram-design@diagram-design`で内訳も確認できた
(スキル7個: `diagram-design`/`doctor`/`export-diagram`/`import-drawio`/`import-excalidraw`/
`import-mermaid`/`profile`、エージェント・フック・MCPサーバーは0個)。

### `self_check.py`を実際に実行し、手動適用との差分を確認した

インストールされたプラグインに同梱の`self_check.py`(Windows環境では`PYTHONUTF8=1`が無いと
ヘルプ表示で`UnicodeEncodeError`になったため指定)を、本検証で作った2つのHTMLに対して実行した。

```
$ python3 self_check.py after-diagram-design.html before-mermaid.html
OK after-diagram-design.html
FAIL before-mermaid.html
  - remote reference on <script>: https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js
  - diagram file needs at least one accessible (non-aria-hidden) SVG
  - at most one script is allowed; found 2
  - script 1 must carry only the canonical data-diagram-controls attribute
  - script 2 must carry only the canonical data-diagram-controls attribute
  - expected exactly one data-motion-root; found 0
```

**手動適用で作った`after-diagram-design.html`は、公式の自動チェックに実際に合格した(OK)。**
手で1項目ずつ確認した§9 Pre-Output Checklistの結果と、ツールによる自動判定が一致したことになる。
比較用の`before-mermaid.html`(そもそもdiagram-designの出力ではない)は想定通りFAILで、
CDN参照・複数script・motion root不在など、単一ファイル完結の要件を満たしていないことが
機械的にも確認できた。

### 同梱サンプルの不整合も、自動チェックでは検出されないことがわかった

本編で「同梱サンプル`example-swimlane.html`は`overflow-x: auto`ラッパーを満たしていない」と
指摘した点について、同じ`self_check.py`をこのサンプルファイル自体にかけてみた。

```
$ python3 self_check.py example-swimlane.html
OK example-swimlane.html
```

**`self_check.py`はこのサンプルをOK判定する。** つまり、本編で見つけた不整合はSKILL.md §9の
チェックリスト(人間/エージェントが目視で確認する前提の文書)の方にしか書かれておらず、
`self_check.py`(README/SKILL.mdが「リポジトリ本体のゲート`lint-skin.py`/`verify-motion.py`の
縮小版」と明記している自動スクリプト)のチェック項目には含まれていない、という切り分けができた。
自動チェックと人間向けチェックリストの間に、互いにカバーしきれていない項目がある
(「自動チェック=完全な正解」ではない)ことが、実際に両方を実行して初めてわかった。

## ファイル一覧

- `after-diagram-design.html` — diagram-design skillの指示を手動適用して作ったスイムレーン図
- `after-diagram-design.png` — 上記のスクリーンショット
- `before-mermaid.html` — 比較用の素のMermaid版(CDN参照、今回の環境では単体では動かない可能性がある点に注意)
- `before-mermaid.png` — 素のMermaid版のスクリーンショット(ローカルmermaid.min.jsで描画)
