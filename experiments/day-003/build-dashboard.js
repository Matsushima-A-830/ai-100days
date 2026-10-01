'use strict';
/**
 * Day 003 検証スクリプト
 *
 * 「AIエージェントに指示してスプレッドシートのダッシュボードを自動生成させる」を、
 * ブラウザもUIも使わずNode.jsのheadlessモードだけで実際に動かす。
 *
 * 出典: https://github.com/dream-num/univer (Apache-2.0)
 * 使用パッケージ: @univerjs/presets@1.0.3, @univerjs/preset-sheets-node-core@1.0.3
 */

const { createUniver, LocaleType } = require('@univerjs/presets');
const { UniverSheetsNodeCorePreset } = require('@univerjs/preset-sheets-node-core');

// Before: AIエージェントが素朴にJSONで返しがちな「生データ」(構造も計算式も無い)
const rawRows = [
  { date: '2026-09-28', product: 'ノートPC', amount: 128000 },
  { date: '2026-09-28', product: 'マウス', amount: 2400 },
  { date: '2026-09-29', product: 'ノートPC', amount: 96000 },
  { date: '2026-09-29', product: 'キーボード', amount: 8800 },
  { date: '2026-09-30', product: 'モニター', amount: 34500 },
];

async function main() {
  const t0 = Date.now();

  const { univerAPI } = createUniver({
    locale: LocaleType.JA_JP,
    locales: {},
    presets: [UniverSheetsNodeCorePreset()],
  });

  const workbook = univerAPI.createWorkbook({ name: 'day-003-sales-dashboard' });
  const sheet = workbook.getActiveSheet();

  // ヘッダー行
  const headers = ['日付', '商品', '売上'];
  headers.forEach((h, i) => {
    sheet.getRange(0, i).setValue(h);
  });
  // ヘッダーを太字にする(facadeのスタイルAPI)
  sheet.getRange(0, 0, 1, headers.length).setFontWeight('bold');

  // データ行
  rawRows.forEach((row, i) => {
    const r = i + 1;
    sheet.getRange(r, 0).setValue(row.date);
    sheet.getRange(r, 1).setValue(row.product);
    sheet.getRange(r, 2).setValue(row.amount);
  });

  // 合計行: SUM式をセットして、headlessのformulaエンジン(ワーカーなし=同期実行)が
  // 実際に計算するかを検証する
  const totalRowIndex = rawRows.length + 1;
  sheet.getRange(totalRowIndex, 1).setValue('合計');
  sheet.getRange(totalRowIndex, 1, 1, 1).setFontWeight('bold');
  const sumRange = `C2:C${rawRows.length + 1}`;
  sheet.getRange(totalRowIndex, 2).setValue({ f: `=SUM(${sumRange})` });

  // 式が非同期(マイクロタスク/コマンドキュー経由)で評価されるのを待つ
  async function waitForFormula(maxWaitMs) {
    const deadline = Date.now() + maxWaitMs;
    while (Date.now() < deadline) {
      const cell = sheet.getRange(totalRowIndex, 2).getCellData();
      if (cell && cell.v !== undefined && cell.v !== null && cell.f) {
        return cell;
      }
      await new Promise((r) => setTimeout(r, 50));
    }
    return sheet.getRange(totalRowIndex, 2).getCellData();
  }

  const totalCell = await waitForFormula(3000);
  const elapsedMs = Date.now() - t0;

  const expectedTotal = rawRows.reduce((s, r) => s + r.amount, 0);
  const headerCell = sheet.getRange(0, 0).getCellData();

  // スナップショット(IWorkbookData)をJSONとして書き出せるかも確認する
  const snapshot = workbook.save();
  const fs = require('fs');
  fs.writeFileSync(__dirname + '/workbook-snapshot.json', JSON.stringify(snapshot, null, 2));

  const result = {
    elapsedMs,
    cellsWritten: headers.length + rawRows.length * 3 + 2,
    headerCellValue: headerCell ? headerCell.v : null,
    headerCellBold: headerCell ? headerCell.s : null,
    totalCellRaw: totalCell,
    totalCellValue: totalCell ? totalCell.v : null,
    expectedTotal,
    formulaMatches: totalCell ? totalCell.v === expectedTotal : false,
    snapshotSheetCount: snapshot.sheetOrder ? snapshot.sheetOrder.length : null,
    snapshotCellA1: (() => {
      const sheetId = snapshot.sheetOrder[0];
      const cellData = snapshot.sheets[sheetId].cellData;
      return cellData && cellData[0] ? cellData[0][0] : null;
    })(),
  };

  console.log(JSON.stringify(result, null, 2));
  process.exit(0);
}

main().catch((err) => {
  console.error('FAILED');
  console.error(err && err.stack ? err.stack : err);
  process.exit(1);
});
