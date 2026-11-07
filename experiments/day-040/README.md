# Day 040: NVIDIA/auto-ontology — Routine環境の制約によりローカル検証が必要

対象: https://github.com/NVIDIA/auto-ontology (Apache-2.0)
確認したcommit: `git clone --depth 1` 時点のdefaultブランチ先頭(2026-11-07取得)。

## ローカル検証(実施済み・2026-11-07)

人間のローカルPCで、build.nvidia.comの無料枠nvapi-キーを使い、Docker Compose + DuckDB1
エンジン構成でBefore/After比較を実施した。詳細は[results.md](./results.md)参照。

- Docker Composeフルスタック(Postgres+pgvector、バックエンド、フロントエンド、
  ingestion service)の起動に成功。
- オントロジー生成(Semantic Compilation)は完走したが、サンプルDB(FK制約未宣言)では
  semantic FK edgeが0件のまま終わった。
- 素朴なtext-to-SQL(スキーマのみをLLMに渡す単発呼び出し)は1回で正しいSQL・正しい
  答えに到達。
- auto-ontology経由のChat UIは、最終的に同じ正しい答えにたどり着いたが、3回のSQL生成が
  存在しない列名を参照して失敗し、自己修正ループで到達するまでに11分33秒かかった。
- 既定モデル(`nvidia/nemotron-3.5-lightning-30b-a3b`)が`langchain_nvidia_ai_endpoints`
  の構造化出力(`guided_json`)に対応しておらず、ほぼ全てのLLM呼び出しステップで
  400エラー→リトライ→reasoning LLMへのフォールバック、というオーバーヘッドが発生し、
  所要時間11分33秒の大半を占めた。

以下はRoutine環境でのエスカレーション時点の記録(当時の制約の記述として残す)。

today.mdの検証スコープ・手順(1〜5)のうち、**手順3「オントロジー生成〜MCPサーバー経由の
自然言語→SQL変換」および手順4「Before/After比較」は、このRoutine無人実行環境固有の
制約により実行できなかった。** 推測で結果を埋めることも「失敗」として書くこともせず、
CLAUDE.mdの方針に従ってローカル検証にエスカレーションする。

## 遭遇した制約(このRoutine環境固有、ツール自体の問題ではない)

### 1. Dockerデーモンが起動していない

`docker` CLI自体はこの実行環境にインストールされている(`docker --version` →
`Docker version 29.9.2`)が、デーモンに接続できない。

```
$ docker pull postgres:17
failed to connect to the docker API at unix:///var/run/docker.sock; check if the
path is correct and if the daemon is running: dial unix /var/run/docker.sock:
connect: no such file or directory
```

auto-ontologyはアプリ自身のメタデータ・カタログ・オントロジー・ベクトルストアを
Postgres + pgvectorに保存する構成が前提(`docs/connections.md`、README「Software
Components」参照)で、これはDuckDB等の軽量な接続先エンジンを選んでも避けられない
(DuckDB/SQLiteは「問い合わせ対象」の選択肢であり、アプリ本体のDBはPostgres固定)。
Docker Composeでこの最小構成(Postgres+pgvector、バックエンド、フロントエンド)を
立てられないと、ingestion・オントロジー生成・チャットのいずれも検証できない。

today.mdの検証手順1で事前に想定されていた「Dockerが使えない場合」のケースに該当する。

### 2. LLM推論用のAPIキーが本Routine環境に一つも設定されていない

auto-ontologyはオントロジー生成・NL→SQL変換・埋め込み・リランクの全てでLLM呼び出しが
必須(`.env.example`の`DEFAULT_MODELS_API_KEY`等)。既定はbuild.nvidia.comの無料枠
nvapi-キーだが、OpenAI互換エンドポイントを指定すれば他プロバイダのキーでも代替できる
構成になっている。そこで主要プロバイダの環境変数を確認したが、**いずれも未設定**だった
(値は出力せず、設定有無のみ確認):

```
$ [ -n "$DEFAULT_MODELS_API_KEY" ] && echo set || echo unset
unset
$ [ -n "$NVIDIA_API_KEY" ] && echo set || echo unset
unset
$ [ -n "$NVAPI_KEY" ] && echo set || echo unset
unset
$ for v in OPENAI_API_KEY ANTHROPIC_API_KEY GEMINI_API_KEY OPENROUTER_API_KEY TOGETHER_API_KEY GROQ_API_KEY; do
    [ -n "${!v}" ] && echo "$v: set" || echo "$v: unset"; done
OPENAI_API_KEY: unset
ANTHROPIC_API_KEY: unset
GEMINI_API_KEY: unset
OPENROUTER_API_KEY: unset
TOGETHER_API_KEY: unset
GROQ_API_KEY: unset
```

ローカルLLM(Ollama)も未インストール(`which ollama`→該当なし、`:11434`への接続も失敗)。
build.nvidia.comの無料枠nvapi-キーの取得自体は人間によるアカウント登録(メール確認等)を
伴う操作であり、本Routineが無人のまま代わりに行うべき操作ではないと判断した。

いずれの制約も、ツール自体の既定設定・公式手順に不備があるわけではなく、
本クラウドRoutine実行環境固有の制約(Dockerデーモン非対応、外部キー未登録)である。
そのためCLAUDE.mdの方針(書かない: Routine環境の制約)に従い、articles/posts/cardsは
今回作成していない。

## できた範囲の確認(読み取りのみ)

- `git clone --depth 1`でリポジトリを取得し、`LICENSE`がApache-2.0であることを確認した。
- README・`docs/connections.md`・`.env.example`・`auto_ontology/connectors/duckdb.py`を
  読み、アーキテクチャ(Next.jsフロントエンド+FastAPIバックエンド+Postgres/pgvector、
  ingestion workerの4コンポーネント)と、DuckDBは`CONNECTION_STRINGS=duckdb://...`で
  問い合わせ対象として指定できる(サーバー不要・UIからの追加は不可)ことを確認した。
  ただしこれはコードを読んだだけで、実行して確認したわけではない。

## ローカル検証の再現手順(人間向け)

today.mdの検証スコープ(DuckDB1エンジンに絞る)に従う前提の手順。

1. build.nvidia.com で無料枠のnvapi-キーを取得する(課金設定はしない)。
2. リポジトリをclone して `.env` を作成する。

   ```bash
   git clone https://github.com/NVIDIA/auto-ontology.git
   cd auto-ontology
   cp .env.example .env
   ```

3. `.env` を編集する。最低限、以下を設定する(他のAPIキー行は削除してDEFAULT_MODELS_*に
   フォールバックさせてよい)。

   ```dotenv
   DEFAULT_MODELS_API_KEY=nvapi-...   # build.nvidia.comで取得した無料枠キー
   AUTH_SECRET=<openssl rand -base64 32の出力>
   POSTGRES_PASSWORD=<新しいパスワード>
   AUTO_ONTOLOGY_ADMIN_PASSWORD=<新しいパスワード>
   PGADMIN_PASSWORD=<新しいパスワード>
   # 問い合わせ対象をDuckDBに絞る(today.mdのスコープ)。パスは後述のサンプルDBを指す。
   CONNECTION_STRINGS=duckdb:///絶対パス/sample.duckdb
   ```

4. サンプルのDuckDB(数テーブル程度)を自分で用意する。例:

   ```bash
   python3 -c "
   import duckdb
   con = duckdb.connect('sample.duckdb')
   con.execute('CREATE TABLE customers (id INTEGER, name VARCHAR, state VARCHAR)')
   con.execute(\"INSERT INTO customers VALUES (1,'Alice','PA'),(2,'Bob','CA')\")
   con.execute('CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount DECIMAL, month VARCHAR)')
   con.execute(\"INSERT INTO orders VALUES (1,1,120.5,'2026-06'),(2,2,80.0,'2026-06')\")
   "
   ```

5. Postgres(アプリ本体のメタデータ・カタログ・ベクトルストア用)を起動し、残りのスタックを
   ビルド・起動する。

   ```bash
   docker compose up -d --wait postgres
   docker compose up -d --build
   ```

6. `http://localhost:3000` を開き、`AUTO_ONTOLOGY_ADMIN_EMAIL` / `AUTO_ONTOLOGY_ADMIN_PASSWORD`
   でログインし、**Settings → Semantic Compilation** をONにしてオントロジー生成を待つ。

7. Chatで同じ質問を2通りの方法で試し、Before/Afterを記録する。
   - **Before(素朴なtext-to-SQL)**: auto-ontologyを使わず、スキーマ定義だけをLLMに渡して
     直接SQLを生成させる(別スクリプトで、このRoutineが作ったサンプルDuckDBのスキーマを
     LLMに渡すだけの簡単な比較コードを書く)。
   - **After(auto-ontology経由)**: Chat UI(またはMCPサーバー)に同じ質問をし、生成された
     SQL・参照したテーブル/カラム・provenanceを記録する。
   - 誤ったテーブル/カラム参照の有無を比較する。

8. 実行コマンド・出力・所要時間を`results.md`に追記する。失敗した場合もそのまま記録する。

結果が出たら、`results.md`を更新し、CLAUDE.mdの命名規則(`articles/day-040-<英語slug>.md`、
12〜50文字・frontmatter必須)に従ってZenn記事・`posts/x/day-040.md`・`posts/note/day-040.md`・
`posts/cards/day-040.html`(`tools/card-template.html`から複製)を作成する。
