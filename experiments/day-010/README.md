# Day 010: REA (morluto/rea) を自作Electronアプリで検証

対象: https://github.com/morluto/rea (MIT, npm: `rea-agents@5.0.0`)

詳しい経緯・つまずき・実測値は `results.md` を参照。ここでは再現手順のみをまとめる。

**注意**: 本検証は筆者が自作した `sample-app/`(MIT表記・本リポジトリに同梱)のみを対象にしている。
第三者の著作物・商用ソフトウェアの解析は行っていない。また `rea setup` は実行していない
(このセッションのグローバルなエージェント設定を書き換えてしまうため)。CLIを直接呼び出す、
README/skillドキュメントが明記している正式なフォールバック経路のみを使用した。

## 再現手順

```bash
# 1. Node.js v22.19+ または v24.11+ が必要(rea-agents@5.0.0のengines指定)
node --version   # v22.22.0 で確認済み

# 2. rea-agents をインストールせず npx で直接実行(追加のAPIキー・GPU不要)
cd experiments/day-010

# 2-1. 静的JS/Electron解析(MCP登録・Hopper・Ghidra不要)
npx -y rea-agents@latest analyze-javascript-application ./sample-app --format json \
  > rea-output/analyze-javascript-application.json

# 2-2. IPCチャンネル名を起点に機能トレース(seedの形式はresults.md 4-1節参照)
#   application には上の出力全体をそのまま埋め込む
npx -y rea-agents@latest trace-application-feature rea-output/wf-feat-coupon_debug.json \
  --format json > rea-output/trace-coupon-debug-channel.json

# 2-3. 環境診断(今回のタスクで意味を持つのは node/host のみ。Hopper/Ghidra/IDAは未使用なので
#      healthy: false のままで問題ない)
npx -y rea-agents@latest doctor --json > rea-output/doctor.json

# 2-4. (失敗を確認した例) 読みやすいソース復元は外部ツール(Wakaru)が別途必要で今回は未インストール
npx -y rea-agents@latest recover-javascript-sources "$(pwd)/sample-app" "$(pwd)/rea-output/recovered" \
  --format json
```

## sample-app/ の正解(ground truth)

`sample-app/lib/pricing.js` の `_q(code, subtotal)` は以下の割引ロジック(筆者が書いたので既知):

| 条件 | 割引 |
|---|---|
| `code`が`VIP-`で始まり、文字コード合計 mod 7 が0 | 50%オフ |
| `code`が`VIP-`で始まり、mod 7が0以外 | 15%オフ |
| `VIP-`で始まらず、mod 7が3 | 一律$10オフ |
| それ以外 | 割引なし |

`main.js`には`ipcMain.handle('coupon:debug', ...)`という、`process.env.COUPON_DEBUG === '1337'`の
ときだけ内部状態を返す隠しデバッグチャンネルもある。REAの解析結果とこの正解をどこまで一致させられたかは
`results.md`で詳述している。

## 生成物

- `sample-app/` — 検証対象の自作Electronアプリ(MIT)
- `rea-output/` — REAの各コマンドの実行結果(JSON)。`analyze-javascript-application.json`が約1.3MBあるため
  記事・カードには要約した数値のみを引用し、全文はこのディレクトリに保存している。
