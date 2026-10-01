# Day 003: Univerのheadless(Node.js)モードでAIエージェントがスプレッドシートを生成できるか検証する

## これは何か

GitHub Trendingで急上昇していたOSS Office SDK「Univer」(Apache-2.0、
https://github.com/dream-num/univer )は、「AIエージェント向けのオフィスハーネス」を
標榜し、ブラウザUIを介さずNode.jsだけでワークブックを生成・編集できる
"Headless Univer" モードを公式にサポートしている
(README内に `Headless for AI infrastructure` という記載あり)。

この「ブラウザもGPUもAPIキーも無しで、AIエージェントがコードだけでExcel的な
ダッシュボードを組み立てられる」という主張を、実際に手を動かして検証した。

外部APIキー・GPUは不要。npm registryからのパッケージ取得のみ外部通信を使用。

## 対象コードのライセンス・出典について

- 検証対象: Univer (https://github.com/dream-num/univer), Apache-2.0
- 使用した公開パッケージ: `@univerjs/presets@1.0.3`, `@univerjs/preset-sheets-node-core@1.0.3`
  (いずれもnpm上で `"license": "Apache-2.0"`)
- `build-dashboard.js` / `perf-scaling.js` はこの検証のためにゼロから書いた
  オリジナルコードで、Univer本体のソースコードは転載していない。

## ディレクトリ構成

```
experiments/day-003/
├── README.md             (このファイル)
├── results.md             実行ログ・結果・実際に踏んだエラーの記録
├── build-dashboard.js     Before/After検証スクリプト(生データ→計算済みダッシュボード)
├── perf-scaling.js        行数を増やしたときのスケーリング検証スクリプト
├── run1.log, run2.log     build-dashboard.jsの実行ログ(2回分)
├── perf-scaling.log       perf-scaling.jsの実行ログ
├── workbook-snapshot.json build-dashboard.js実行時の実際のスナップショットJSON
└── package.json           依存関係(@univerjs/presets, @univerjs/preset-sheets-node-core, rxjs)
```

## 再現手順

前提: Node.js >= 18.17 (検証時はv22.22.0で実行)。

```bash
cd experiments/day-003
npm install

# Before/After検証(ヘッダー太字 + SUM式の計算をheadlessで確認)
node build-dashboard.js

# スケーリング検証(10〜3000行でSUM式の計算時間を実測)
node perf-scaling.js
```

`build-dashboard.js` は実行のたびに `workbook-snapshot.json` を上書きする。
スタイルID(`s`フィールドの文字列)はスタイルプールの採番なので実行のたびに
変わるが、計算結果(`formulaMatches: true`)やセルの値は再現する。

## 結果の要約

詳細は `results.md` を参照。要点だけ書くと:

- ブラウザ・DOM無しのNode.jsプロセス内で、ヘッダーの太字スタイル設定・
  複数セルへのデータ書き込み・`SUM`式の計算が実際に動いた(2回実行して再現)。
- 行数を3000行まで増やしてもSUM式の計算結果は毎回期待値と完全一致した
  (ただし `createWorkbook({})` のデフォルトは1000行までで、超えると
  `Range is out of bounds` で実際に落ちた。`setRowCount()` で明示的に拡張して解決)。
- 日付文字列をセットしただけでExcel形式の日付シリアル値に自動変換される、
  という狙っていなかった挙動も実際のスナップショットJSONから発見した。
- today.md/backlog.mdに書かれていた「Worktree機能」は、インストールした
  パッケージにもUniver本体のリポジトリにも見当たらず、**検証できなかった**
  (results.mdに調査過程を記録)。
