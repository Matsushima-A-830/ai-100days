---
title: "OSS Office SDK「Univer」のheadless(Node.js)モードでAIエージェントがダッシュボードを作れるか試した"
emoji: "📊"
type: "tech"
topics: ["ai", "nodejs", "opensource", "spreadsheet", "javascript"]
published: true
---

## きっかけ

GitHub Trendingで急上昇していたOSSの「Office SDK」、Univer
(https://github.com/dream-num/univer, Apache-2.0)が気になった。
スプレッドシート・ドキュメント・スライドを1つのランタイムで扱え、READMEには

> **Headless for AI infrastructure**
> Run workbook and document logic in Node.js to power agents, automation, and server-side workflows.

と、はっきり「AIエージェント向け」を謳っている。「ブラウザもGPUもAPIキーも無しで、
AIエージェントがコードだけでExcel的なダッシュボードを組み立てられる」という主張を、
筆者自身の手(このセッション内のコード実行)で確かめてみた。

- 出典: https://github.com/dream-num/univer
- ライセンス: Apache-2.0(npm上の `@univerjs/presets` / `@univerjs/preset-sheets-node-core` も同じく明記)
- 日本語記事: Qiitaに「Univer入門」記事が1件あるのみで、headlessモードに踏み込んだ
  日本語記事は見当たらなかった(2026-09-30時点でZenn 0件)。

外部APIキー・GPUは不要。npm registryからのパッケージ取得のみ外部通信を使用した。

## やったこと

1. Node.js(ブラウザ・DOM無し)で、Univerの"Headless"用プリセットパッケージを
   使ってワークブックを生成し、ヘッダーの太字設定・データ書き込み・`SUM`式の計算を
   実際に動かす
2. 行数を増やしながら(10〜3000行)、書き込み+式計算にかかる時間を実測する
3. today.md/backlog.mdのメモにあった「Worktree機能」が実在するか調べる

検証コード一式は `experiments/day-003/` に置いてある。

## セットアップ

```bash
npm install @univerjs/presets@1.0.3 @univerjs/preset-sheets-node-core@1.0.3 rxjs
```

重要なのは、`@univerjs/preset-sheets-node-core` の依存関係に
**`@univerjs/engine-render`(ブラウザ描画エンジン)が含まれていない**こと。
jsdomのようなDOMシムは一切不要で、素のNode.jsプロセスだけで動く設計になっている
(モノレポの `docs/ISOMORPHIC.md` にも「Node.jsのサポートはブラウザと同じ優先度」
と明記されていた)。

## 検証1: 生データ→計算済みダッシュボード(Before/After)

AIエージェントが素朴に返しがちな「構造も計算式も無い生データ」をイメージして、
以下のような配列を用意した。

```js
const rawRows = [
  { date: '2026-09-28', product: 'ノートPC', amount: 128000 },
  { date: '2026-09-28', product: 'マウス', amount: 2400 },
  { date: '2026-09-29', product: 'ノートPC', amount: 96000 },
  { date: '2026-09-29', product: 'キーボード', amount: 8800 },
  { date: '2026-09-30', product: 'モニター', amount: 34500 },
];
```

これをUniverのFacade API(`FUniver`)経由で、ヘッダー太字+`=SUM(C2:C6)`式入りの
ダッシュボードに組み立てる。

```js
const { univerAPI } = createUniver({
  locale: LocaleType.JA_JP,
  locales: {},
  presets: [UniverSheetsNodeCorePreset()],
});
const workbook = univerAPI.createWorkbook({ name: 'day-003-sales-dashboard' });
const sheet = workbook.getActiveSheet();

sheet.getRange(0, 0, 1, 3).setFontWeight('bold'); // ヘッダー太字
// ...データ書き込み...
sheet.getRange(totalRowIndex, 2).setValue({ f: '=SUM(C2:C6)' });
```

実行結果(`node build-dashboard.js`、生ログは `experiments/day-003/run1.log`):

```json
{
  "elapsedMs": 198,
  "totalCellRaw": { "f": "=SUM(C2:C6)", "v": 269700, "t": 2 },
  "expectedTotal": 269700,
  "formulaMatches": true
}
```

`128000+2400+96000+8800+34500 = 269700` と完全一致。2回目の実行(`run2.log`)でも
`elapsedMs: 172`、`formulaMatches: true` で再現した。

ポイントは、Workerスレッド用の `workerSrc` を一切指定していないのに式が
正しく計算されたこと。`@univerjs/preset-sheets-node-core` のソースを読むと、
`workerSrc` を渡さない場合は `UniverFormulaEnginePlugin` が
`notExecuteFormula: false` になり、メインスレッドで同期的に式を評価する
実装になっている。つまり「とりあえず動かしてみる」だけなら、ワーカー周りの
セットアップは不要だった。

### 狙っていなかった発見: 日付の自動型推論

太字スタイルがJSONスナップショットにどう残るか確認するため `workbook.save()` の
出力を覗いていたら、`"2026-09-28"` という文字列でセットしたはずの日付セルが

```json
{ "v": 46293, "s": "z3usvb", "t": 2 }
```

という、Excel形式の**日付シリアル値**+日付表示用のスタイルに自動変換されていた。
`1899-12-30` を起点に `46293` 日を足すと `2026-09-28` になることをPythonで検算し、
確かに元の日付と一致することを確認した。ブラウザUIを介さないheadlessモードでも、
セル書き込みの型推論ロジックは共通で効いているらしい。

## 検証2: 行数を増やしたときのスケーリング

ヘッダー+データ+`SUM`式を、行数を変えながら書き込んで計算完了までの時間を測った
(`experiments/day-003/perf-scaling.js`)。

| 行数 | 書き込みセル数 | 所要時間(ms) | SUM式が期待値と一致 |
|---:|---:|---:|:---:|
| 10 | 24 | 172 | ✓ |
| 100 | 204 | 85 | ✓ |
| 500 | 1,004 | 197 | ✓ |
| 1,000 | 2,004 | 341 | ✓ |
| 3,000 | 6,004 | 562 | ✓ |

全ケースでSUM式の計算結果はJS側で別途計算した期待値と完全一致した。

### 実際に踏んだエラー

最初に3000行のケースを流したとき、1000行目に書き込もうとしたところで
以下の例外が出てスクリプトが落ちた。

```
Error: Range is out of bounds. Max rows: 1000, Max columns: 20,
Given range: {"startRow":1000,"endRow":1000,...}
    at new FRange (.../@univerjs/sheets/lib/cjs/facade.js:4466:142)
```

原因は `createWorkbook({})` で作られるデフォルトシートが「1000行×20列」までしか
無いこと。`sheet.setRowCount(rowCount + 10)` で明示的に行数を拡張することで解決した。
AIエージェントに任意サイズの表を生成させるユースケースでは、素朴に
`createWorkbook({})` だけ呼ぶと1000行の壁に当たるので注意が必要、という
地味だが実用上は大事な制約だと感じた。

## 検証できなかったこと: 「Worktree機能」

今回のbacklogメモには「Worktree機能(人間レビュー前の下書き分離)も余裕があれば
触れる」と書いていたが、実際に

- インストールした `@univerjs/*` パッケージ一式を `grep -rli worktree`
- Univer本体のGitHubリポジトリの `README.md` / `CHANGELOG.md` を `grep -i worktree`

した結果、**どちらもヒットしなかった**。OSS版のドキュメント・コードベースの
どこにも「Worktree」という名前の機能は見当たらず、元のメモが別の文脈の情報と
混同していた可能性がある。動かしていないものを動いたと書くわけにはいかないので、
この記事では「検証できなかった」とだけ記録しておく。

## まとめ

- Univerの"Headless"プリセット(`@univerjs/preset-sheets-node-core`)は、
  ブラウザ・DOM無しのNode.jsだけでスタイル設定・セル書き込み・式計算が
  実際に動いた。APIキー・GPUも不要。
- 日付の自動型推論など、ドキュメントだけでは気づかなかった挙動も
  スナップショットJSONを実際に覗いて発見できた。
- 一方で、デフォルトのシートサイズ制限(1000行)のような、使ってみて初めて
  分かる制約もあった。
- backlogにあった「Worktree機能」は、今回調べた範囲では実在を確認できなかった。

検証コード・実行ログ・スナップショットJSONはすべて `experiments/day-003/` に
置いてあるので、気になる方は再現してみてほしい。
