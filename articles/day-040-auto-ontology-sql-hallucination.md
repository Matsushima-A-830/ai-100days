---
title: "NVIDIA/auto-ontologyを動かしたら、素朴なtext-to-SQLより遅く間違えた"
emoji: "🗂️"
type: "tech"
topics: ["ai", "llm", "sql", "nvidia", "docker"]
published: false
---

## これは何を試した記事か

NVIDIAが公開している[auto-ontology](https://github.com/NVIDIA/auto-ontology)(Apache-2.0)は、データベースのメタデータから「オントロジー」(ビジネス用語・テーブル関係・SQL属性の集合)を自動生成し、AIエージェントが自然言語の質問を正確なSQLに変換できるようにするフレームワークである。
README・モデルカードが掲げる価値は明快で、「エージェントが誤ったテーブル/カラムを参照してSQLを生成してしまう問題」を、事前に構築したオントロジーの知識で防ぐ、というものだ。

筆者はこれを実際にDocker Composeで自分のPCに構築し、2テーブルだけの小さなサンプルDuckDBに対して、素朴なtext-to-SQL(スキーマをLLMに渡すだけの単発呼び出し)とauto-ontology経由のChat UIで、同じ質問を投げてBefore/Afterを比較した。
結論を先に書くと、**今回のような小規模でFK制約を宣言していないデータベースでは、auto-ontologyは素朴なtext-to-SQLより誤ったSQL生成が多く、所要時間も圧倒的に長くなった。**
原因は大きく2つあり、1つはこのツール固有の挙動(小規模DBでのFK検出)、もう1つは`.env.example`の既定モデル設定とライブラリ側の実装の不整合という、ツールの設定不備だった。

- 出典: https://github.com/NVIDIA/auto-ontology (Apache-2.0)
- 日本語記事件数(2026-11-07時点、Zenn/Qiita/note検索): 0件

## セットアップで最初につまずいた2点

公式の`.env.example`をコピーし、build.nvidia.comで取得した無料枠のnvapi-キーを設定して、サンプルのDuckDB(`customers`/`orders`の2テーブル)を用意した。
ここで2つの、公式ドキュメントに書かれていない落とし穴に当たった。

### DuckDBファイルのバージョン不一致

`pip install duckdb`で素直に最新版(2.0.0系、storage version 999)を入れてサンプルDBを作ったところ、auto-ontologyのコンテナ内は`duckdb==1.5.5`(storage versionは64〜68系)で、こんなエラーになった。

```
_duckdb.IOException: IO Error: Trying to read a database file with version number 999,
but we can only read versions between 64 and 68.
The database file was created with an newer version of DuckDB.
```

コンテナと同じ`duckdb==1.5.5`をローカルにも入れ直し、サンプルDBを作り直して解決した。

### Dockerコンテナからホストのファイルが見えない

`CONNECTION_STRINGS=duckdb:///絶対パス`でホストのファイルパスをそのまま指定しても、Dockerコンテナは別のファイルシステムを持つため、当然ながら見えない。

```
_duckdb.IOException: IO Error: Cannot open database "/home/.../sample.duckdb" in
read-only mode: database does not exist
```

`docker-compose.override.yml`でホストのDuckDBファイルをコンテナの`/data/`にbind mountし、`CONNECTION_STRINGS=duckdb:////data/sample.duckdb`に変更して解決した。
`docs/connections.md`にはDocker利用時のDuckDBファイルのマウント方法が明記されておらず、自分で気づく必要があった。

これらを解決すると、Postgres+pgvector・バックエンド・フロントエンド・ingestion serviceの5サービスすべてが`healthy`で起動し、`http://localhost:3000`のログイン画面にたどり着けた。

## オントロジー生成: FK関係が1件も検出されなかった

Settings画面の「Enable Semantic Compilation」をONにすると、即座にコンパイルが走った。

```
Semantic calculation finished successfully (database='sample')
  — 2 table(s), 0 semantic FK edge(s), 0 SqlAttribute(s), 0 bridge table(s) in 376.3s
```

**`orders.customer_id`→`customers.id`という、2テーブルしかない中で唯一のFK関係が、1件も検出されなかった。**
サンプルDuckDBにFOREIGN KEY制約を明示的に宣言していなかったため宣言的FKが0件なのは想定どおりだが、LLM/埋め込みベースの推論でも検出されなかった。
ingestion中、埋め込み呼び出し(`nvidia/nemotron-3.5-embed-1b`)が断続的に`500 service inference failed`で失敗しており、埋め込みが欠けたことで類似度ベースのFK推定が働かなかった可能性がある。
このエンドポイント自体は無効ではなく(同じキーで単発のテストリクエストは`200`で成功した)、無料枠の埋め込みエンドポイントが並行リクエストに弱い、という挙動に見えた。

## Before: 素朴なtext-to-SQL

auto-ontologyを使わず、スキーマ定義だけをLLM(auto-ontologyと同じ`nvidia/nemotron-3.5-lightning-30b-a3b`)に渡し、単発のchat completions呼び出しでSQLを生成させた。

```sql
-- 「どの州の注文合計額が最も高いか、その合計額は?」に対する生成結果(そのまま)
SELECT c.state, SUM(o.amount) AS total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY c.state
ORDER BY total_amount DESC
LIMIT 1;
```

**1回の生成で、実在する列名のみを使った正しいSQLが得られた。**
サンプルDuckDBに対して実行すると`CA, 280`(正解)。所要時間は数秒、API呼び出しは1回のみ。

## After: auto-ontology経由(Chat UI)

同じ質問をChat UIに投げた。
最終的には正しい答え(`CA, 280`)にたどり着いたが、そこに至るまでに4回のSQL生成・実行サイクルのうち3回が、存在しない列名を参照して失敗した。

| 試行 | 生成されたSQL(抜粋) | 結果 |
|---|---|---|
| 1 | `... FROM orders AS o GROUP BY o.state ...` | 失敗: `orders`に`state`列は無い |
| 2 | `... JOIN customers AS c ON o.customer_id = c.customer_id ...` | 失敗: `customers`に`customer_id`列は無い(正しくは`id`) |
| 3 | `... SUM(o.order_amount) ... JOIN customers AS c ON o.customer_id = c.id ...` | 失敗: `orders`に`order_amount`列は無い(正しくは`amount`) |
| 4 | `SELECT c.state, SUM(o.amount) ... JOIN customers AS c ON o.customer_id = c.id GROUP BY c.state ...` | **成功**: `CA, 280` |

実際のエラーメッセージ(2回目の例、そのまま)。

```
_duckdb.BinderException: Binder Error: Table "c" does not have a column named "customer_id"
Candidate bindings: : "id"
```

各試行は、DuckDBから返る実際のエラーメッセージ(存在する列候補付き)をLLMにフィードバックして次のSQLを再生成する、自己修正ループで進んでいた。
つまり今回は、**オントロジー(意味的なスキーマ知識)ではなく、DBの実行時エラーメッセージを手がかりにした試行錯誤で正解にたどり着いていた。**
これは前節で確認した「semantic FK edge: 0」(FK関係がオントロジーに未登録)と整合する挙動である。

### 所要時間は11分33秒

チャットのリクエストから最終応答まで、ログ上で**11分33秒**かかった。
内訳の大半はSQL生成の試行錯誤そのものではなく、**ほぼ全てのLLM呼び出しステップで発生していた、以下の400エラーとそのフォールバック**だった。

```
Exception: [400] unknown field `guided_json`, expected one of `greed_sampling`,
`use_raw_prompt`, `annotations`, `backend_instance_id`, ...
```

`.env.example`の既定モデル`nvidia/nemotron-3.5-lightning-30b-a3b`は、auto-ontologyが使う`langchain_nvidia_ai_endpoints`ライブラリが構造化出力(JSON Schema強制)を要求する際に送る`guided_json`パラメータを、NVIDIA-hosted APIエンドポイント側が認識せず`400 Bad Request`を返す。
これは予見されていなかった問題ではなく、モデル読み込み時点でauto-ontology自身が次の警告を出している。

```
UserWarning: Model 'nvidia/nemotron-3.5-lightning-30b-a3b' is not known to support
structured output. Your output may fail at inference time.
```

non-reasoning LLM呼び出しは3回リトライ後にreasoning LLM(既定では同一モデル)へフォールバックし、そちらは成功する、というパターンがテキストtoSQLグラフの各ノード(9ノード以上)で繰り返された。
これが数十秒ずつ積み重なり、11分超の大半を占めていた。

## まとめ

| | Before(素朴なtext-to-SQL) | After(auto-ontology) |
|---|---|---|
| 最終的な正答 | ○(`CA, 280`) | ○(`CA, 280`、ただし試行錯誤の末) |
| 誤ったSQL生成 | 0回 | 3回(存在しない列名を参照) |
| 所要時間 | 数秒 | 11分33秒 |
| 必要なセットアップ | APIキーのみ | Docker Composeフルスタック、オントロジー事前生成 |

- ライセンス(Apache-2.0)、アーキテクチャ(Next.js+FastAPI+Postgres/pgvector)は確認済み。
- 今回の最小構成(2テーブル・FK制約未宣言のサンプルDB)では、auto-ontologyの狙い(「オントロジーが列参照の誤りを防ぐ」)が実際には機能しなかった。オントロジー生成時にFK関係が1件も検出されなかったため、NL→SQL変換の際も素のLLMと同程度に列名を推測に頼ることになった。
- `.env.example`の既定モデルが、auto-ontology自身が使うライブラリの構造化出力機能と噛み合わないという設定不備があり、これが所要時間11分33秒の大半を占めていた。
- これは「auto-ontologyが無意味」という結論ではない。FK制約が宣言されている、あるいは埋め込みベースのFK推定が正常に機能するより大きなデータベースでは結果が変わる可能性が高い。今回確認できたのは、小規模・FK未宣言のデータベースと、既定モデル設定という、2つの具体的な条件下での挙動である。
