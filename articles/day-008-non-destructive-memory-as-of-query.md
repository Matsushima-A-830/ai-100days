---
title: "「要約して上書きするメモリ」は過去の正しさを答えられない、を自作コードで確かめた"
emoji: "🗄️"
type: "tech"
topics: ["ai", "llm", "agent", "postgresql", "rag"]
published: false
---

## 要約

組織向けLLMエージェントの「記憶」フレームワークである[Mem++](https://arxiv.org/abs/2610.02002)(コード: [AIDAChip-Inc/mem-plus-plus](https://github.com/AIDAChip-Inc/mem-plus-plus)、Apache-2.0)を検証対象に選んだ。売りは「書き込み時に要約・圧縮して古い記録を上書きしない」非破壊メモリで、一般的なエージェントメモリ(Mem0やZepなど)が苦手な「過去のある時点では何が正しかったか」という質問に強い、という主張だ。

結論から書くと、**今回も実リポジトリ本体のコードは実行できなかった**。GitHubスター3個というまだ実績の薄い新規プロジェクトのコードを、Claude Codeが動いているクラウド実行環境の安全機構が「外部コードの実行」としてブロックしたためだ。本連載では[Day 007](https://zenn.dev/matsu/articles/day-007-claim-vs-execution-log-gap)でも同種の壁にぶつかっており、今回も同じ壁だった。

そこで、READMEと論文で説明されているアルゴリズムの考え方——日付フィルタ+複数indexの検索+直近優先スロットという「読み込み時に選ぶ」設計——を理解した上で、筆者が独自に書いた最小限のPythonコードで、「要約・上書き型メモリ」と「非破壊型メモリ」の違いを確かめた。

## Mem++とは何か

Mem++は、Slackのスレッドやメール・議事録・チケットなど、複数人が書き込み、更新し、時には矛盾させる「組織の記録」を対象にしたLLMエージェント向けメモリフレームワークだ。一般的なエージェントメモリの多くは「1人のユーザーが自分のことを語る」会話メモリ向けに作られていて、書き込み時にLLMで要約・抽出し、抽出し損ねた情報は消える。Mem++はその逆を行く。

- 書き込み時にLLM呼び出しをせず、記録をそのまま日付・著者付きで保存する(append-only)。
- 読み込み時に、字句検索(PostgreSQLの全文検索)・ベクトル検索(pgvector)・エンティティタグ検索の3つのindexを重み付きRRF(Reciprocal Rank Fusion)で統合し、さらに直近の記録向けに数枠を確保する。
- `occurred_at <= θ`という日付フィルタをベースクエリに持つため、「θ時点では何が正しかったか」という質問にそのまま答えられる。

論文はこれを**OrgMemBench**という443アーティファクト・157スレッド・18ヶ月分・73問のベンチマークで評価し、既存手法を8.0〜13.1ポイント上回ると報告している(今回は未検証)。

## つまずき: 実リポジトリのセットアップがブロックされた

まず`git clone`は問題なく通り、READMEやLICENSE(Apache-2.0)、`pyproject.toml`を読むところまでは支障がなかった。READMEのQuickstartが要求する「PostgreSQL 16 + pgvector」という土台も、実際に用意できた。

```
$ apt-get install -y postgresql-16-pgvector
Setting up postgresql-16-pgvector (0.6.0-1) ...

$ pg_ctlcluster 16 main start
$ sudo -u postgres psql -c "CREATE DATABASE memplusplus;"
CREATE DATABASE
$ sudo -u postgres psql -d memplusplus -c "CREATE EXTENSION vector;"
CREATE EXTENSION
```

ところが、READMEの指示通りcloneしたディレクトリ内で`uv sync`を実行しようとしたところ、以下の拒否が返ってきた。

```
Permission for this action was denied by the Claude Code auto mode classifier.
Reason: [Code from External].
```

Day 007のK-Dense BYOKの件と全く同じ種類の制約で、「まだ実績の薄い新規OSSのコードを自動実行Routineが無審査でローカルにインストール・実行すること」への安全策だ。拒否メッセージは別の方法での迂回も明示的に禁じていたので、`pip install`や直接`import memory`のような別経路は試さなかった。結果として、**ONNX MiniLM埋め込み・pgvectorでのベクトル検索・RRF融合といったMem++本体の実装は一切動かせていない。**

せっかく用意したPostgreSQL+pgvectorの環境は、結局この後の自作の最小再現コードでは使わなかった(標準ライブラリのみで十分だったため)。環境構築自体はできたのに本題では使えなかった、というのも含めて正直に書いておく。

## 代わりにやったこと: 自作の最小再現コードでアルゴリズムの考え方だけを比較する

実リポジトリを動かせない以上、Mem++そのものの性能を検証したとは言えない。そこで、せめてMem++が解決しようとしている核心の問題——「要約・上書き型メモリはas-ofクエリ(過去のある時点を問う質問)に原理的に弱い」——を、自分で書いたPythonコードで最小再現した。

架空の社内決定記録データセットを3トピック×3回更新=9件用意した。

```python
Record("search", "全文検索基盤はElasticsearchを採用する。", ["search", "elasticsearch"], date(2024, 2, 1), "tanaka"),
Record("search", "運用コストの都合でElasticsearchからOpenSearchに移行する。", ["search", "opensearch"], date(2024, 9, 15), "tanaka"),
Record("search", "追加クラスタ運用をやめ、Postgres全文検索(tsvector)に一本化する。", ["search", "postgres"], date(2025, 6, 1), "sato"),
# (cloud, review も同様に各3回更新)
```

比較した2つの実装はどちらも筆者の独自実装で、実リポジトリのコードには依存していない。

- `DestructiveSummaryMemory`: トピックごとに最新の記録だけを保持し、新しい記録が来ると古い記録への参照を完全に失う。「要約・圧縮して上書きする」従来型メモリのシミュレーション。
- `NonDestructiveMemory`: 記録を一切上書きせず全件保持し、クエリのas_of日付で`occurred_at <= as_of`にフィルタした上で、タグの重なり数→日付の新しさの順で記録を選ぶ。Mem++の「日付フィルタ+直近優先」という考え方の簡易再現であり、実際のts_rank_cd全文検索・pgvector類似度・RRF融合の数値的な詳細は再現していない。

各トピックについて「古い時点」「中間の時点」「現在時点」を問う3クエリ(計9クエリ)を投げた。

```
$ python3 experiments/day-008/compare_memory.py
topic    as_of        destructive nondestructive
search   2024-06-01   NG       OK
    期待: 全文検索基盤はElasticsearchを採用する。
    要約型の回答: 追加クラスタ運用をやめ、Postgres全文検索(tsvector)に一本化する。
search   2025-01-01   NG       OK
search   2026-10-06   OK       OK
cloud    2024-06-01   NG       OK
cloud    2025-03-01   NG       OK
cloud    2026-10-06   OK       OK
review   2024-06-01   NG       OK
review   2025-04-01   NG       OK
review   2026-10-06   OK       OK

destructive_summary accuracy:    3/9 = 33.3%
non_destructive (Mem++-style) accuracy: 9/9 = 100.0%
```

要約型が正解できたのは「現在時点」を聞く3問だけで、過去のある時点を聞く6問すべてで、まだ存在していなかった未来の決定を答えてしまっている(例: 2024年6月時点の検索基盤を聞かれて、2025年6月に決まったPostgres移行を答える)。これは架空データセットなので当然そうなるよう設計した結果であり、驚きのある発見ではない。確認できたのは、「要約・上書き型メモリはas-ofクエリで原理的に過去の状態を再現できない」という、Mem++論文がC3(Bi-temporal as-of capability)として指摘する問題の構造を、小さいが明確な形で再現できた、という点にとどまる。

## 考察

今日もまた、「本体を動かす」という当初の目標には到達できなかった。ただ、2回連続でサンドボックスの安全機構に同じ理由でブロックされたことで、このチャレンジの実行環境における構造的な制約——新規・低実績OSSのインストーラやビルドスクリプトを自動Routineがそのまま実行することはできない、という線——がはっきり見えてきた。今後似た候補を選ぶ際は、「pip経由で素直に入る成熟したパッケージか」「自分でロジックを再現できる単純さか」を事前にbacklog.mdの評価軸に加えた方が良さそうだ。

本体を動かせなかった分、今日の検証は「Mem++というアルゴリズムの検証」ではなく「要約・上書き型メモリという設計そのものの弱点を、最小のコードで目に見える数字(33.3%対100.0%)にする」という、もう一段抽象的な作業になった。Mem++固有の実装(ONNX埋め込み・pgvectorの類似度計算・RRFの重み付け)が実際にどの程度うまく機能するかは、引き続き未検証のまま残っている。

## 出典・ライセンス

- Mem++: [github.com/AIDAChip-Inc/mem-plus-plus](https://github.com/AIDAChip-Inc/mem-plus-plus)(Apache-2.0)
- 論文: [arXiv:2610.02002](https://arxiv.org/abs/2610.02002)
- 実行ログ・自作コード全体: `experiments/day-008/`(`results.md`に生の実行ログと検証の限界、`README.md`に再現手順を記載)
