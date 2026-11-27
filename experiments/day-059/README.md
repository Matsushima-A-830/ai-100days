# Day 059: colbymchenry/codegraph を検証する

## 対象

- https://github.com/colbymchenry/codegraph (MIT License, npm: `@colbymchenry/codegraph`)
- コーディングエージェント(Claude Code, Cursor, Codex CLIなど)向けに、ローカルのSQLiteにシンボル(関数・クラス等)と呼び出し/参照関係を事前インデックスし、MCP経由またはCLIで公開するツール。

## 再現手順

```bash
# リポジトリルートで実行

# 1. インデックス構築(APIキー・GPU不要、完全ローカル)
npx -y @colbymchenry/codegraph init .

# 2. 状態確認
npx -y @colbymchenry/codegraph status .

# 3. 既知の関数の呼び出し元/呼び出し先を調べる
npx -y @colbymchenry/codegraph callers render_frame
npx -y @colbymchenry/codegraph callees render_frame

# 4. クロスファイル・export alias解決の確認
npx -y @colbymchenry/codegraph callers _q      # 見つかる(実体の名前)
npx -y @colbymchenry/codegraph callers quote   # 見つからない(呼び出し側の名前)

# 5. 重複コード検出の限界を確認する最小ケース
#    experiments/day-059/duplicate-test/a.py, b.py に
#    ロジックが同一だが独立実装(呼び出し関係なし)の2関数を用意済み
npx -y @colbymchenry/codegraph sync .
npx -y @colbymchenry/codegraph impact validate_email_signup
npx -y @colbymchenry/codegraph context "refactor email validation logic to share one implementation"

# 6. 汎用的なシンボル名での結果の混入を確認
npx -y @colbymchenry/codegraph explore render_frame main
```

生成される `.codegraph/` ディレクトリ(SQLite DB)はローカルの索引なのでgitignore済み(`.gitignore`に追記済み)。

## 検証スコープ

本リポジトリ(ai-100days)自身(159ファイル、Python/JS/C#/Rust混在)をインデックス対象とした。GPU・APIキーは一切使用していない。

詳細な実行ログと結果は `results.md` を参照。
