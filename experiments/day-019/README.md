# Day 019: xerj-org/xerj をリポジトリ自身に対して動かす

対象: [xerj-org/xerj](https://github.com/xerj-org/xerj) v1.0.0-rc.96 (Apache-2.0)

詳しい結果・考察は [`results.md`](./results.md) を参照。ここでは再現手順のみまとめる。

## 事前準備

- x86_64 Linux(今回はプリビルドバイナリの`x86_64-unknown-linux-gnu`を使用)
- 追加の有料APIキーは不要。既定(lexical)モードはGPU不要。
  `--embed-mode neural`はCPUでも動くが非常に低速(本検証では3〜6KB/s)。

## 再現手順

```bash
# 1. 公式プリビルドバイナリを取得(データディレクトリ・ログは
#    インデックス対象フォルダの外、例: /tmp に置くこと。詳細はresults.md 2節)
mkdir -p /tmp/xerj-runtime/bin /tmp/xerj-runtime/data
curl -sSL -o /tmp/xerj.tar.gz \
  https://github.com/xerj-org/xerj/releases/download/v1.0.0-rc.96/xerj-1.0.0-rc.96-x86_64-unknown-linux-gnu.tar.gz
tar xzf /tmp/xerj.tar.gz -C /tmp/xerj-runtime/bin --strip-components=1

# 2. サーバー起動(--insecureはローカル検証用。本番では使わない)
/tmp/xerj-runtime/bin/xerj --insecure --data-dir /tmp/xerj-runtime/data --port 9200 &

# 3. 対象フォルダをautoindex(サーバーに対してHTTP経由で実行)
/tmp/xerj-runtime/bin/xerj autoindex /path/to/your/repo --url http://localhost:9200

# 4. 検索・symbol検索
/tmp/xerj-runtime/bin/xerj search "調べたい語句"
/tmp/xerj-runtime/bin/xerj def "symbol_name"

# 5. MCPサーバーをstdioで直接叩く(initialize → tools/list → tools/call)
#    実際に使ったPythonプローブはsamples/配下のログに結果のみ保存。
/tmp/xerj-runtime/bin/xerj mcp --url http://localhost:9200
```

## このディレクトリの内容

- `results.md` — 検証の過程・結果・見つかった挙動の詳細
- `samples/01〜04` — `autoindex`実行時に実際に踏んだ4つのエラー・拒否の
  ログ(フラグ名の誤り、自己言及的な失敗、削除検知による拒否、
  embedding空間混在の拒否)
- `samples/05` — `xerj def`の多言語symbol検索(Python/C/Rust)とJS非対応の確認
- `samples/06` — MCP経由での自己診断ヒント(`_xerj.hints`)の実例
- `samples/07` — `--embed-mode neural`でも小規模コーパスでは
  `semantic_text`にならない現象の再現ログ
- `samples/08` — MCPツール一覧(16個)と、semantic_textが有効な
  インデックスでの意味ベース検索の実例

## MCP経由ではなくstdio直叩きで検証した理由

`xerj init`はプロジェクトスコープの`.mcp.json`等を生成する安全な設計だが、
生成後に「エージェントの再起動が必要」と明記されている。無人実行のRoutineは
自分自身を再起動できないため、実際の書き込みは`--dry-run`での確認のみに
留め、`xerj mcp`(既に起動しているノードにstdio経由でプロキシするだけの
コマンド)を直接起動してJSON-RPCを送ることでMCPツール自体の動作を検証した。
詳細は`results.md` 5節を参照。
