# Day 018: morluto/rea (REA) で「素性非公開」のminified JSを解析させる

対象: [morluto/rea](https://github.com/morluto/rea) (npm: `rea-agents`, MIT) v6.5.0

詳しい結果・考察は [`results.md`](./results.md) を参照。ここでは再現手順のみまとめる。

**スコープ:** 静的なJavaScript解析のみ。Hopper/Ghidra/IDA等の商用ツールを使うネイティブバイナリ解析は
今回のスコープ外(未検証)。

## 事前準備

- Node.js 22系以上(今回は22.22.0で検証。package.json上は`>=24.18.0 <25`を要求しているが実行は可能だった)
- 追加の有料APIキー・GPUは不要

## 再現手順

```bash
# 1. REAのバージョン確認・ヘルスチェック
npx -y rea-agents@latest --version
npx -y rea-agents@latest doctor

# 2. 解析対象を用意する(ここではjQuery 3.7.1のビルド済みminifiedファイルを
#    「素性非公開のアプリ」として模すため、ライセンスコメントを取り除いて使用)
mkdir -p /tmp/work && cd /tmp/work
npm init -y
npm install jquery@3.7.1 --no-save
mkdir -p blind-target
python3 -c "
data = open('node_modules/jquery/dist/jquery.min.js', encoding='utf-8').read()
idx = data.index('*/')
open('blind-target/bundle.js', 'w', encoding='utf-8').write(data[idx+2:].lstrip('\n'))
"
echo '{"name":"mystery-app","version":"1.0.0"}' > blind-target/package.json

# 3. 静的解析(analyze-javascript-application)
npx -y rea-agents@latest analyze-javascript-application ./blind-target --format json > analyze-out.json

# 4. コード復元(recover-javascript-sources)には外部ツール Wakaru が別途必要
npm install wakaru@1.14.0 --no-save
export REA_WAKARU_COMMAND="$(pwd)/node_modules/@wakaru/cli-linux-x64/wakaru"
npx -y rea-agents@latest recover-javascript-sources \
  "$(pwd)/blind-target/bundle.js" "$(pwd)/recovered" --format json

# 5. 復元結果を確認
cat recovered/modules/module.js
node --check recovered/modules/module.js   # 構文チェック
```

## このディレクトリの内容

- `results.md` — 検証の過程・結果・見つかった不具合の詳細
- `samples/bundle.js` — 検証に使った「素性を隠した」jQuery 3.7.1 minifiedファイル(87,444 bytes)
- `samples/recovered-module.js` — REA + Wakaruが復元した読みやすいコード(6,341行、191,015 bytes)
  - **注意:** このファイルには `results.md` 3-4節で報告した通り、343行目に実際のNULバイトが
    含まれている。テキストエディタによっては正しく表示されない場合がある。
- `samples/manifest.json`, `samples/wakaru-report.json`, `samples/wakaru-provenance.json`
  — `recover-javascript-sources` 実行時にREAが生成したメタデータ
- `samples/analyze-javascript-application-summary.json` — 静的解析結果の要約
  (元の`semantic_graph`は約40MBあるため全文はリポジトリに含めていない)

## MCP経由ではなくCLI直接実行で検証した理由

`npx rea-agents setup` はこのセッション自身が使っているClaude Codeのグローバル設定ファイル
(`/root/.claude.json`、リポジトリ外)を書き換え、反映にはクライアント再起動が必要になる。
無人実行のRoutineはこれを安全に行えないため、MCP登録は行わず、MCPツールと同じ実装を呼ぶ
CLIサブコマンド(`rea analyze-javascript-application` 等)を直接実行して検証した。
詳細は `results.md` 1節を参照。
