# Day 008 検証結果: Mem++(非破壊メモリ)

- 対象: Mem++ — https://arxiv.org/abs/2610.02002 / https://github.com/AIDAChip-Inc/mem-plus-plus (Apache-2.0)
- 検証日: 2026-10-06
- 結論を先に書く: **実リポジトリのコードは実行できなかった**。サンドボックスの安全分類器に
  ブロックされたため。代わりに、論文/READMEで説明されているアルゴリズムの考え方
  (日付フィルタ+複数indexによる検索+直近優先スロット、という「読み込み時に選ぶ」設計)を
  理解した上で、**筆者が独自に書いた最小再現コード**で「要約・上書き型メモリ」と
  「非破壊(as-ofフィルタ)型メモリ」の違いを比較した。実リポジトリ自体の性能(論文のOrgMemBenchの
  8.0〜13.1ポイント差など)を再現したわけではない点に注意。

## 1. 実施した手順と、実際に起きたこと(正直な記録)

### 1-1. リポジトリのclone — 成功

```
$ git clone https://github.com/AIDAChip-Inc/mem-plus-plus.git
Cloning into 'mem-plus-plus'...
```
clone自体は成功し、README・LICENSE(Apache-2.0確認)・pyproject.tomlなどを読めた。

### 1-2. PostgreSQL 16 + pgvector のセットアップ — 成功

実行環境にはPostgreSQL 16がインストール済みだったが、systemdが無いコンテナのため
サービスが起動していなかった。`pg_ctlcluster`で起動し、pgvector拡張はaptで追加インストールした。

```
$ apt-get install -y postgresql-16-pgvector
...
Setting up postgresql-16-pgvector (0.6.0-1) ...

$ pg_ctlcluster 16 main start
(→ pg_lsclusters: 16  main    5432 online postgres /var/lib/postgresql/16/main ...)

$ sudo -u postgres psql -c "CREATE DATABASE memplusplus;"
CREATE DATABASE
$ sudo -u postgres psql -d memplusplus -c "CREATE EXTENSION vector;"
CREATE EXTENSION
```

ここまでは、READMEが要求する「PostgreSQL 16 + pgvector」という土台自体は実際に用意できた。

### 1-3. 実リポジトリの依存関係インストール(`uv sync`) — ブロックされた

Mem++本体を動かすため、cloneしたディレクトリ内で`uv sync`(READMEのQuickstartの通り)を
実行しようとしたところ、Claude Codeのサンドボックス側の安全分類器に拒否された。

```
$ cd mem-plus-plus && uv sync
→ Permission for this action was denied by the Claude Code auto mode classifier.
  Reason: [Code from External].
```

これは「GitHubスター3個のまだ実績が薄い新規リポジトリ」(backlog.mdにも記載した注意点)の
コードを、ローカルにインストール・実行することに対する安全側の制限であり、`pip install`や
直接`import memory`のような別経路で同じ結果(外部リポジトリのコードの実行)を迂回することも
許可されていない。そのため、**今回はMem++本体のコードは一行も実行していない**。
(day-007のK-Dense BYOKがサンドボックスにブロックされた件と同種の制約。)

### 1-4. 方針転換: 自作の最小再現コードでアルゴリズムの考え方だけを検証

READMEの「How it works」節(日付フィルタ→lexical/vector/tagの3indexをRRFで統合→直近3件を
優先スロットで確保、という設計)を読んだ上で、実リポジトリのコードには依存しない
`compare_memory.py`を独自に書いた。中身は以下の2つの最小実装の比較:

- `DestructiveSummaryMemory`: トピックごとに最新の記録だけを保持し、新しい記録が来ると
  古い記録への参照を完全に失う(=「要約・圧縮して上書きする」従来型メモリのシミュレーション)。
- `NonDestructiveMemory`: 記録を一切上書きせずに全件保持し、クエリのas_of日付で
  `occurred_at <= as_of`にフィルタした上で、タグの重なり数→日付の新しさの順で最良の記録を選ぶ
  (Mem++の「日付フィルタ+index選択+直近優先」という考え方の簡易再現。実際の
  ts_rank_cd全文検索・pgvector類似度・RRF融合・7日半減期などの数値的な詳細は再現していない)。

架空の社内決定記録データセット(検索基盤・デプロイ先クラウド・コードレビュー方針の3トピック、
各3回更新=計9件、日付・著者付き)を用意し、各トピックについて
「古い時点」「中間の時点」「現在時点」の3つのas-ofクエリ(計9クエリ)を投げて正答率を比較した。

## 2. 実行結果(そのままの出力)

```
$ python3 experiments/day-008/compare_memory.py
topic    as_of        destructive nondestructive
search   2024-06-01   NG       OK      
    期待: 全文検索基盤はElasticsearchを採用する。
    要約型の回答: 追加クラスタ運用をやめ、Postgres全文検索(tsvector)に一本化する。
search   2025-01-01   NG       OK      
    期待: 運用コストの都合でElasticsearchからOpenSearchに移行する。
    要約型の回答: 追加クラスタ運用をやめ、Postgres全文検索(tsvector)に一本化する。
search   2026-10-06   OK       OK      
cloud    2024-06-01   NG       OK      
    期待: 新規サービスのデプロイ先はAWSとする。
    要約型の回答: 社内のML基盤統合に合わせてAzureに移行する。
cloud    2025-03-01   NG       OK      
    期待: コスト最適化のためGCPへ移行する。
    要約型の回答: 社内のML基盤統合に合わせてAzureに移行する。
cloud    2026-10-06   OK       OK      
review   2024-06-01   NG       OK      
    期待: コードレビューは必ず2人の承認を必要とする。
    要約型の回答: Lintボットを信頼し、人間レビューは1人承認のみで良いとする。
review   2025-04-01   NG       OK      
    期待: レビュー負荷が高いため、1人承認+Lintボットの自動チェックに変更する。
    要約型の回答: Lintボットを信頼し、人間レビューは1人承認のみで良いとする。
review   2026-10-06   OK       OK      

destructive_summary accuracy:    3/9 = 33.3%
non_destructive (Mem++-style) accuracy: 9/9 = 100.0%
```

要約型は「現在時点」を問う3クエリ(各トピック1つ、計3/9)にしか正答できず、過去のある時点を
問う6クエリすべてで、実際には「まだ存在していなかった未来の情報」を答えてしまっている
(例: 2024年6月時点の検索基盤を聞かれて2025年6月に決定したPostgres移行を答えてしまう)。
これは架空データセットなので当然そうなるよう設計した結果であり、驚きのある発見ではない。
確認できたのは「要約・上書き型メモリはas-ofクエリで原理的に過去の状態を再現できない」という、
Mem++論文がC3(Bi-temporal as-of capability)として指摘している問題の構造を、
小さいが明確な形で再現できた、という点にとどまる。

## 3. 今回の検証の限界(正直な範囲の明記)

- **実リポジトリの性能・挙動は検証していない。** `uv sync`がブロックされたため、ONNX MiniLM埋め込み・
  pgvectorでのベクトル検索・PostgreSQL全文検索のts_rank_cd・RRF融合・consolidation機能など、
  Mem++本体の実装は一切動かしていない。OrgMemBenchでの8.0〜13.1ポイント差という論文の主張も
  未検証のまま。
- 自作コードの「非破壊メモリ」はタグの完全一致ベースの単純なスコアリングであり、
  実際のMem++が行う語彙検索・意味検索の組み合わせではない。
- データセットは筆者が作った9件のみの架空データで、OrgMemBench(443アーティファクト・73問)
  とは規模も性質も全く異なる。
- 比較対象の「要約型ベースライン」も筆者の簡易実装であり、実世界の要約型メモリ実装
  (Mem0やZep等)そのものではない。

## 4. 検証に使った環境

- PostgreSQL 16.14 + pgvector 0.6.0(セットアップはできたが、最終的な比較実験では未使用。
  `compare_memory.py`は標準ライブラリのみで動作する純Pythonスクリプト)
- Python 3.11.15(リポジトリ側のrequires-python>=3.13は`uv sync`がブロックされたため無関係)
- 有料APIキーは使用していない(ANTHROPIC_API_KEY・OPENAI_API_KEYともに未設定・未使用)

## 5. 追記: 「過去だけ正解、現在だけ不正解」のメモリも同じ仕組みで作れるか(`compare_memory_embargo.py`)

本編の結果(要約・上書き型は「現在」3/3正解・「過去」6/6不正解)の逆、つまり
「過去は分かるが現在だけはわざと分からない」メモリが、同じ非破壊+as_ofフィルタの
延長で作れるかを試した。`NonDestructiveMemory`と全く同じ選択ロジックに、
**「取り込み締切(ingestion_cutoff)より新しい記録はそもそも保持時点で除外する」**
という1行だけを足した`EmbargoedMemory`を実装した(実世界でいう日次バッチ取り込みや、
承認待ちで未確定の記録のシミュレーション)。

```
$ python3 experiments/day-008/compare_memory_embargo.py
ingestion_cutoff = 2025-05-24 (today=2026-10-06 - 500days)

topic    as_of        nondestructive   embargoed
search   2024-06-01   OK               OK
search   2025-01-01   OK               OK
search   2026-10-06   OK               NG
    期待:         追加クラスタ運用をやめ、Postgres全文検索(tsvector)に一本化する。
    embargo型の回答: 運用コストの都合でElasticsearchからOpenSearchに移行する。
cloud    2024-06-01   OK               OK
cloud    2025-03-01   OK               OK
cloud    2026-10-06   OK               NG
    期待:         社内のML基盤統合に合わせてAzureに移行する。
    embargo型の回答: コスト最適化のためGCPへ移行する。
review   2024-06-01   OK               OK
review   2025-04-01   OK               OK
review   2026-10-06   OK               NG
    期待:         Lintボットを信頼し、人間レビューは1人承認のみで良いとする。
    embargo型の回答: レビュー負荷が高いため、1人承認+Lintボットの自動チェックに変更する。

nondestructive accuracy: 9/9 = 100.0%
embargoed accuracy:      6/9 = 66.7%
  内訳: 過去クエリ 6/6 、「現在」クエリ 0/3
```

狙い通り、**過去を問う6クエリは全問正解、「現在」を問う3クエリは全問不正解**という、
本編の要約・上書き型とちょうど鏡写しの結果になった。過去クエリが正解なのは、必要な記録が
すべて締切より前に起きているため。「現在」クエリが全滅するのは、本当の最新記録
(2025年6〜8月に起きたもの)が締切(2025-05-24)より後で、EmbargoedMemoryにまだ
取り込まれておらず、1つ前の古い記録を返してしまうため。

これにより、「要約・上書き型メモリが現在にしか強くない」のは設計上の欠陥である一方、
「過去にしか強くないメモリ」は意図的な制約(取り込み遅延・embargo)として普通に作れる、
という非対称性が確認できた。後者は実在のアーキテクチャパターン(日次ETL、法的な
凍結期間、承認後に確定する社内ナレッジベースなど)に対応する。
