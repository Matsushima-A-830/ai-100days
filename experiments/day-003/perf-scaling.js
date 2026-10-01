'use strict';
/**
 * Day 003 追加検証: 行数を増やしたときにheadless Univerでの書き込み+SUM式計算が
 * どれくらいの時間で終わるかを実測する(AIエージェントが大きめのシートを生成する
 * 想定のスケーラビリティ確認)。
 */

const { createUniver, LocaleType } = require('@univerjs/presets');
const { UniverSheetsNodeCorePreset } = require('@univerjs/preset-sheets-node-core');

async function runForRowCount(rowCount) {
  const t0 = Date.now();
  const { univerAPI } = createUniver({
    locale: LocaleType.JA_JP,
    locales: {},
    presets: [UniverSheetsNodeCorePreset()],
  });
  const workbook = univerAPI.createWorkbook({ name: `perf-${rowCount}` });
  const sheet = workbook.getActiveSheet();
  // デフォルトは1000行までしか無く、超えると "Range is out of bounds" で例外になる
  // (実際にrowCount=1000のケースで一度踏んだ)。必要行数+余白まで明示的に広げる。
  if (rowCount + 10 > 1000) {
    sheet.setRowCount(rowCount + 10);
  }

  sheet.getRange(0, 0).setValue('商品');
  sheet.getRange(0, 1).setValue('売上');

  let expectedTotal = 0;
  for (let i = 0; i < rowCount; i++) {
    const amount = (i % 97) * 123 + 100;
    expectedTotal += amount;
    sheet.getRange(i + 1, 0).setValue(`商品${i}`);
    sheet.getRange(i + 1, 1).setValue(amount);
  }

  const totalRow = rowCount + 1;
  sheet.getRange(totalRow, 0).setValue('合計');
  sheet.getRange(totalRow, 1).setValue({ f: `=SUM(B2:B${rowCount + 1})` });

  const deadline = Date.now() + 10000;
  let cell = null;
  while (Date.now() < deadline) {
    cell = sheet.getRange(totalRow, 1).getCellData();
    if (cell && cell.f && cell.v !== undefined && cell.v !== null) break;
    await new Promise((r) => setTimeout(r, 20));
  }

  const elapsedMs = Date.now() - t0;
  return {
    rowCount,
    cellsWritten: rowCount * 2 + 4,
    elapsedMs,
    formulaValue: cell ? cell.v : null,
    expectedTotal,
    formulaMatches: cell ? cell.v === expectedTotal : false,
  };
}

async function main() {
  const sizes = [10, 100, 500, 1000, 3000];
  const results = [];
  for (const n of sizes) {
    const r = await runForRowCount(n);
    results.push(r);
    console.log(JSON.stringify(r));
  }
  console.log('---SUMMARY---');
  console.log(JSON.stringify(results, null, 2));
  const allMatch = results.every((r) => r.formulaMatches);
  console.log('all formulas matched expected sum:', allMatch);
  process.exit(allMatch ? 0 : 1);
}

main().catch((err) => {
  console.error('FAILED');
  console.error(err && err.stack ? err.stack : err);
  process.exit(1);
});
