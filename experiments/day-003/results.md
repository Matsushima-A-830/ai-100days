# Day 003 検証結果

対象: Univer (https://github.com/dream-num/univer, Apache-2.0)
検証内容: 「AIエージェントがブラウザもUIも使わず、Node.jsのheadlessモードだけで
スプレッドシートのダッシュボードを生成できるか」を、実際にコードを書いて実行して確認した。

## 環境

- Node.js: v22.22.0 (`node --version`)
- npm: 10.9.4
- OS: Linux (コンテナ内, 実行環境のまま)
- APIキー・GPU: 不要。インターネット接続はnpm registryへのパッケージ取得のみ使用。

## インストールしたパッケージ

```
npm install @univerjs/presets@1.0.3 @univerjs/preset-sheets-node-core@1.0.3 rxjs
```

実際に解決されたバージョン(`npm ls --depth=0`):

```
day-003@1.0.0 /home/user/ai-100days/experiments/day-003
+-- @univerjs/preset-sheets-node-core@1.0.3
+-- @univerjs/presets@1.0.3
`-- rxjs@7.8.2
```

(`added 78 packages, and audited 79 packages in 8s` — `npm fund`で31パッケージが
funding募集中と表示されたが実害なし。`0 vulnerabilities`。)

`@univerjs/core` や `@univerjs/sheets` を直接インストールする必要はなく、
`@univerjs/preset-sheets-node-core` が依存として引き込む。
重要な点として、このheadless用presetパッケージには `@univerjs/engine-render`
(ブラウザ描画エンジン)への依存が**無い**ことを `npm view` の依存関係一覧で確認した。
つまりjsdomなどのDOMシムは一切不要で、素のNode.jsだけで動く。

## 検証1: Before/After — 生データのJSONから計算済みダッシュボードを生成する

スクリプト: `build-dashboard.js`

- Before: AIエージェントが素朴に返しがちな「構造も計算式も無い生データ」(日付・商品・売上の配列)
- After: `createUniver({ presets: [UniverSheetsNodeCorePreset()] })` で取得した
  `univerAPI`(FUniver facade)を使い、ヘッダー行の太字設定・データ書き込み・
  `=SUM(C2:C6)` 式の設定までをNode.jsのコードだけで行う

実行コマンドと実際の出力(`run1.log`, `run2.log` に生ログを保存):

```
$ node build-dashboard.js
{
  "elapsedMs": 198,
  "cellsWritten": 20,
  "headerCellValue": "日付",
  "headerCellBold": "gL7Ub4",
  "totalCellRaw": {
    "f": "=SUM(C2:C6)",
    "v": 269700,
    "t": 2
  },
  "totalCellValue": 269700,
  "expectedTotal": 269700,
  "formulaMatches": true,
  "snapshotSheetCount": 1,
  "snapshotCellA1": {
    "v": "日付",
    "t": 1,
    "s": "gL7Ub4"
  }
}
```

2回目の実行でも再現(`run2.log`、`elapsedMs: 172`、`formulaMatches: true`。
スタイルIDの文字列はスタイルプールの採番なので毎回変わるが実害なし)。

**確認できたこと:**

1. SUM式はワーカースレッド無し(workerSrc未指定)の設定でも、headlessのまま
   **同期的に正しく計算された**(`269700` = `128000+2400+96000+8800+34500` と完全一致)。
   `@univerjs/preset-sheets-node-core` のソース(`presets/packages/preset-sheets-node-core/src/preset.ts`)
   を見ると、`workerSrc` を渡さない場合は `UniverFormulaEnginePlugin` が
   `notExecuteFormula: false` になり、メインスレッドで式を評価する実装になっている。
2. `setFontWeight('bold')` でセットした太字スタイルは、`workbook.save()` で
   書き出したJSONスナップショット内に `styles` プールの `{"bl": 1}` として
   正しく永続化されていた(`workbook-snapshot.json` に実データあり)。
3. **想定していなかった挙動**: 日付を文字列 `"2026-09-28"` としてセットしただけなのに、
   Univerが自動的にExcel形式の日付シリアル値(`46293`)+日付用の表示形式スタイルに
   変換して保存していた。ブラウザUIが無いheadlessモードでも、この手の「型推論」は
   セル書き込みの共通ロジック側で動いていることが分かった(狙って検証した訳ではなく
   スナップショットJSONを覗いて気づいた副産物)。
   - 検算: `date(1899,12,30) + 46293日 = 2026-09-28` (Pythonで計算して一致を確認)。

## 検証2: 行数を増やしたときのスケーリング(数値推移)

スクリプト: `perf-scaling.js`、生ログ: `perf-scaling.log`

行数を 10 / 100 / 500 / 1000 / 3000 と増やしながら、ヘッダー+データ+SUM式を
書き込んで式が正しく評価されるまでの時間を実測した。

```
rowCount=10    cells=24    elapsedMs=172   formula一致=true
rowCount=100   cells=204   elapsedMs=85    formula一致=true
rowCount=500   cells=1004  elapsedMs=197   formula一致=true
rowCount=1000  cells=2004  elapsedMs=341   formula一致=true
rowCount=3000  cells=6004  elapsedMs=562   formula一致=true
```

全ケースでSUM式の計算結果が期待値(JS側で別途計算した合計)と完全一致した。

**実際に踏んだエラー(正直に記録):** 最初 `rowCount=1000` のケースで
`createWorkbook({})` のデフォルト設定のまま1001行目(`totalRow`)に書き込もうとしたところ、
以下のエラーで**スクリプトが落ちた**:

```
Error: Range is out of bounds. Max rows: 1000, Max columns: 20,
Given range: {"startRow":1000,"endRow":1000,"startColumn":0,"endColumn":0,...}
    at new FRange (.../@univerjs/sheets/lib/cjs/facade.js:4466:142)
```

原因は `createWorkbook({})` で作られるデフォルトシートが「1000行 × 20列」までしか
無いこと。`sheet.setRowCount(rowCount + 10)` で明示的に行数を広げることで解決した
(`perf-scaling.js` 内にコメントで残している)。この制約は「AIエージェントに
大きめの表を生成させる」ユースケースでは地味にハマりどころになりそうなので、
記事にもそのまま載せる。

## 検証3(未検証・正直な記録): backlog.mdにあった「Worktree機能」

`today.md`/`backlog.md` には「Worktree機能(人間レビュー前の下書き分離)も
余裕があれば触れる」という補足メモがあったが、以下の通り調査した範囲では
**実在を確認できなかった**:

- インストールした `@univerjs/*` パッケージ一式(`node_modules/@univerjs/`)を
  `grep -rli worktree` した結果、ヒット無し。
- Univer本体のGitHubリポジトリ(`github.com/dream-num/univer`)を浅くクローンし、
  `README.md` / `CHANGELOG.md` を `grep -i worktree` した結果もヒット無し。

Univerには「Snapshot」や将来的な「Collaboration」関連の機能はあるが、
「Worktree」という名前の機能はOSS版のドキュメント・コードベースのどこにも
見当たらなかった。元のbacklogメモが別の製品の機能と混同していた可能性があるため、
**この日の記事では検証していない機能として扱い、「動いた」とは書かない**。

## ライセンス

- Univer本体: Apache-2.0 (`github.com/dream-num/univer` のLICENSEファイルで確認)。
- 今回使用した `@univerjs/presets` / `@univerjs/preset-sheets-node-core` も
  npmのpackage.json上で `"license": "Apache-2.0"` と明記されている。
- 本検証で書いたコード(`build-dashboard.js`, `perf-scaling.js`)はこの検証のために
  ゼロから書いたオリジナルコードで、Univer本体のコードは一切転載していない。

## ファイル一覧

- `build-dashboard.js` — Before/After検証スクリプト
- `perf-scaling.js` — スケーリング検証スクリプト
- `run1.log`, `run2.log` — build-dashboard.jsの実行ログ(2回分)
- `perf-scaling.log` — perf-scaling.jsの実行ログ
- `workbook-snapshot.json` — build-dashboard.js実行時に書き出された実際のスナップショットJSON
- `package.json` / `package-lock.json` — 依存関係の記録
