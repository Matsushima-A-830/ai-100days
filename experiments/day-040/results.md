# Day 040 検証結果 — NVIDIA/auto-ontology

対象: https://github.com/NVIDIA/auto-ontology (Apache-2.0)
検証環境: 人間のローカルPC(Windows 11 + WSL2、Docker Compose、NVIDIA build.nvidia.com無料枠nvapi-キー)
検証日: 2026-11-07

Routine環境ではDockerデーモン非稼働・APIキー未設定によりローカル検証にエスカレーションされた
(詳細は[README.md](./README.md)参照)。今回、人間が実際にDocker Composeで全スタックを起動し、
today.mdのスコープどおりDuckDB1エンジンに絞ってBefore/After比較を実施した。

## 1. ローカル環境のセットアップ

```bash
git clone https://github.com/NVIDIA/auto-ontology.git
cd auto-ontology
cp .env.example .env
# DEFAULT_MODELS_API_KEY に build.nvidia.com の無料枠nvapi-キーを設定
# REASONING_API_KEY/NON_REASONING_API_KEY/EMBED_API_KEY/RERANK_API_KEY は
# プレースホルダーのままだとフォールバックしないためコメントアウトして未設定にした
```

サンプルのDuckDB(customers/orders、2テーブル)を作成。

```python
import duckdb
con = duckdb.connect('sample.duckdb')
con.execute('CREATE TABLE customers (id INTEGER, name VARCHAR, state VARCHAR)')
con.execute("INSERT INTO customers VALUES (1,'Alice','PA'),(2,'Bob','CA'),(3,'Carol','CA')")
con.execute('CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount DECIMAL, month VARCHAR)')
con.execute("INSERT INTO orders VALUES (1,1,120.5,'2026-06'),(2,2,80.0,'2026-06'),(3,3,200.0,'2026-07'),(4,1,50.0,'2026-07')")
```

**つまずき1: DuckDBファイルのバージョン不一致。** `pip install duckdb`で素直に入れると
2.0.0系(storage version 999)になるが、auto-ontologyのコンテナ内は`duckdb==1.5.5`
(storage versionは64〜68系)。新しいduckdbで作ったファイルは
`IO Error: Trying to read a database file with version number 999, but we can only
read versions between 64 and 68.`で読めない。コンテナと同じ`duckdb==1.5.5`を
ローカルにも入れ直して作り直した。

**つまずき2: コンテナにファイルが見えない。** `CONNECTION_STRINGS=duckdb:///絶対パス`で
ホストのパスをそのまま指定しても、Dockerコンテナ内からはそのパスは存在しない(別ファイル
システム)。`docker-compose.override.yml`でホストのDuckDBファイルをコンテナの`/data/`に
bind mountし、`CONNECTION_STRINGS=duckdb:////data/sample.duckdb`に変更して解決した。
公式ドキュメント(`docs/connections.md`)にはDocker利用時のDuckDBファイルのマウント方法が
明記されておらず、自分で気づく必要があった。

```yaml
# docker-compose.override.yml
services:
  auto-ontology:
    volumes:
      - /home/<user>/day040-work/sample.duckdb:/data/sample.duckdb
  ingestion-service:
    volumes:
      - /home/<user>/day040-work/sample.duckdb:/data/sample.duckdb
```

```bash
docker compose up -d --wait postgres
docker compose up -d --build
```

5サービス(postgres, auto-ontology, auto-ontology-frontend, ingestion-service, pgadmin)
すべて`healthy`で起動した。`http://localhost:3000`でログイン画面が表示され、
`AUTO_ONTOLOGY_ADMIN_EMAIL`/`AUTO_ONTOLOGY_ADMIN_PASSWORD`でログインできた。

## 2. オントロジー生成(Semantic Compilation)

Settings → Semantic Compilationで「Enable Semantic Compilation」をONにすると、即座に
コンパイルが走った。

```
ingest: finished successfully — 1 connection(s) ingested in 165.8s
  (2 table(s), 7 column(s), 0 embedding row(s) — embeddingは後述の理由で失敗)
Semantic calculation finished successfully (database='sample')
  — 2 table(s), 0 semantic FK edge(s), 0 SqlAttribute(s), 0 bridge table(s) in 376.3s
```

**ingestion中の埋め込み呼び出しが断続的に`500 service inference failed`で失敗した。**
`DEFAULT_MODELS_API_KEY`自体は有効(直接curlで簡単なリクエストを送ると`200`が返る)
なので、キー自体の問題ではなく、埋め込みエンドポイント(`nvidia/nemotron-3.5-embed-1b`、
無料枠)側の一時的な過負荷/不安定さに見える。アプリ側は4回までリトライして諦め、
「このラウンドでは埋め込み0件」として処理を続行した(クラッシュはしない)。

**`orders.customer_id`→`customers.id`のFK関係は検出されなかった(semantic FK edge: 0)。**
今回のサンプルDuckDBには明示的なFOREIGN KEY制約を付けていなかったため、宣言的FK (0件)
は想定どおりだが、LLM/埋め込みベースの推論でも1件も検出されなかった。原因は上記の
埋め込み呼び出し失敗が関係している可能性がある(埋め込みが無ければ類似度ベースの
FK推定ができない)。この「FK関係をオントロジーが把握していない」状態が、次節の
NL→SQL変換の結果に直接影響した。

## 3. Before: 素朴なtext-to-SQL(auto-ontology不使用)

スキーマ定義だけをLLM(`nvidia/nemotron-3.5-lightning-30b-a3b`、auto-ontologyと同じ
モデル)に渡し、単発のchat completions呼び出しでSQLを生成させた。

```python
prompt = f"""You are a SQL generator. Given this schema:
CREATE TABLE customers (id INTEGER, name VARCHAR, state VARCHAR);
CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount DECIMAL, month VARCHAR);

Write a single SQL query (DuckDB dialect) to answer this question:
Which state had the highest total order amount, and what was that total?
"""
```

実際の出力(そのまま):

```sql
SELECT c.state, SUM(o.amount) AS total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY c.state
ORDER BY total_amount DESC
LIMIT 1;
```

**1回の生成で、実在する列名のみを使った正しいSQLが得られた。** サンプルDuckDBに対して
実行すると `CA, 280` (正解)。所要時間は数秒、API呼び出しは1回のみ。

## 4. After: auto-ontology経由(Chat UI)

Chat UIに同じ質問「Which state had the highest total order amount, and what was that
total?」を投げた。バックエンドのログをそのまま追跡した。

**結果: 最終的に正しい答え(`CA, 280`)にたどり着いたが、そこまでに4回のSQL生成・実行
サイクルのうち3回が存在しない列名を参照して失敗した。**

| 試行 | 生成されたSQL(抜粋) | 結果 |
|---|---|---|
| 1 | `... FROM orders AS o GROUP BY o.state ...` | 失敗: `orders`に`state`列は無い(`customers`側の列) |
| 2 | `... JOIN customers AS c ON o.customer_id = c.customer_id ...` | 失敗: `customers`に`customer_id`列は無い(正しくは`id`) |
| 3 | `... SUM(o.order_amount) ... JOIN customers AS c ON o.customer_id = c.id ...` | 失敗: `orders`に`order_amount`列は無い(正しくは`amount`) |
| 4 | `SELECT c.state, SUM(o.amount) AS total_order_amount FROM orders AS o JOIN customers AS c ON o.customer_id = c.id GROUP BY c.state ORDER BY total_order_amount DESC LIMIT 1;` | **成功**: `CA, 280` |

実際のエラーメッセージ(2回目の例、そのまま):

```
_duckdb.BinderException: Binder Error: Table "c" does not have a column named "customer_id"
Candidate bindings: : "id"
```

各試行は、DuckDBから返る実際のエラーメッセージ(存在する列候補付き)をLLMにフィードバック
して次のSQLを再生成する、という自己修正ループ(`sql_execution` → `invalid_sql` →
`reconstruct_sql` → `validate_sql_query` → `sql_execution` …)で進んでいた。**つまり
今回は、オントロジー(意味的なスキーマ知識)ではなく、DBの実行時エラーメッセージを
手がかりにした試行錯誤で正解にたどり着いていた。** 2節で確認した「semantic FK edge: 0」
(FK関係がオントロジーに未登録)と整合する挙動である。

### 所要時間

チャットのリクエストログ(`Chat completions request`)から最終応答
(`analyze_and_visualize: complete`)まで **11分33秒**(03:09:06 → 03:20:39)。

内訳の大半は、SQL生成そのものではなく、**ほぼ全てのLLM呼び出しステップで発生した
以下の400エラーとそのフォールバック**によるもの:

```
Exception: [400] unknown field `guided_json`, expected one of `greed_sampling`,
`use_raw_prompt`, `annotations`, `backend_instance_id`, ...
```

```
WARNING auto_ontology.utils.llm_invoke: Non-reasoning LLM exhausted 3 retries for
QuestionIntentModel (...) — falling back to reasoning LLM
```

`.env.example`の既定モデル`nvidia/nemotron-3.5-lightning-30b-a3b`は、
`langchain_nvidia_ai_endpoints`が構造化出力(JSON Schema強制、`guided_json`パラメータ)
を要求する際、NVIDIA-hosted APIエンドポイント側がそのパラメータ自体を認識せず
`400 Bad Request`を返す。これはモデル読み込み時点で以下の警告としてauto-ontology自身が
出している、予見されていた問題である。

```
UserWarning: Model 'nvidia/nemotron-3.5-lightning-30b-a3b' is not known to support
structured output. Your output may fail at inference time.
```

non-reasoning LLM呼び出しは3回リトライ後にreasoning LLM(既定では同一モデル)へ
フォールバックし、そちらは(構造化出力の実装経路が異なるためか)成功する、という
パターンがテキストtoSQLグラフの各ノードで繰り返された。これが9ノード以上×数十秒の
累積となり、11分超の大半を占めた。

## 5. まとめ(Before/After比較)

| | Before(素朴なtext-to-SQL) | After(auto-ontology) |
|---|---|---|
| 最終的な正答 | ○(`CA, 280`) | ○(`CA, 280`、ただし試行錯誤の末) |
| 誤ったSQL生成 | 0回 | 3回(存在しない列名を参照) |
| 所要時間 | 数秒 | 11分33秒 |
| APIコール回数 | 1回 | 数十回(構造化出力の400エラー・リトライ含む) |
| 必要なセットアップ | APIキーのみ | Docker Compose(Postgres+pgvector)フルスタック、オントロジー事前生成 |

今回の最小構成(2テーブル・FK制約なしのサンプルDB)では、auto-ontologyの狙い
(「オントロジーが列参照の誤りを防ぐ」)が実際には機能しなかった。オントロジー生成時に
FK関係(`orders.customer_id`→`customers.id`)が1件も検出されなかったため、NL→SQL変換の
際も素のLLMと同程度に列名を推測に頼ることになり、結果として素朴なtext-to-SQLより
**誤ったSQL生成の回数が多く、所要時間も圧倒的に長くなった。** 加えて、`.env.example`の
既定モデルが`langchain_nvidia_ai_endpoints`の構造化出力と噛み合わないという、
ツール自身のデフォルト設定の不整合が所要時間の大半を占めていた。

これは「auto-ontologyが無意味」という結論ではない。FK制約が宣言されている、あるいは
埋め込みベースのFK推定が正常に機能するより大きなデータベースでは、結果が変わる可能性が
高い。今回確認できたのは、**(a) 既定モデルの構造化出力非対応という設定不備、
(b) 小規模・FK未宣言のデータベースではオントロジーのFK検出が機能せず、自己修正ループに
よる試行錯誤コストだけが乗る、という2点の具体的な制約**である。
