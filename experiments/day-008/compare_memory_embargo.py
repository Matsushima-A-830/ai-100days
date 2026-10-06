"""
compare_memory.pyの追加実験: 「非破壊メモリ+as_ofフィルタ」の仕組みに
「直近N日以内に起きた記録はまだ取り込んでいないことにする」という
人為的な取り込み遅延(embargo)を1つだけ足した場合の挙動を確認する。

動機: compare_memory.pyの結果は「要約・上書き型は現在にしか強くない」
(現在3/3正解、過去6/6不正解)だった。これの鏡写しとして、
「過去は分かるが現在だけはわざと分からない」メモリも同じ仕組みの延長で
作れるはずだ、という考察を実際に動かして確認する。

注意: これも筆者独自のコードで、AIDAChip-Inc/mem-plus-plus 本体は使っていない。
EmbargoedMemoryはNonDestructiveMemoryと全く同じロジックで、
「ingestion_cutoffより新しい記録を保持時点で除外する」という1行だけが違う。
"""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class Record:
    topic: str
    content: str
    tags: list[str]
    occurred_at: date
    author: str


RECORDS: list[Record] = [
    Record("search", "全文検索基盤はElasticsearchを採用する。", ["search", "elasticsearch"], date(2024, 2, 1), "tanaka"),
    Record("search", "運用コストの都合でElasticsearchからOpenSearchに移行する。", ["search", "opensearch"], date(2024, 9, 15), "tanaka"),
    Record("search", "追加クラスタ運用をやめ、Postgres全文検索(tsvector)に一本化する。", ["search", "postgres"], date(2025, 6, 1), "sato"),
    Record("cloud", "新規サービスのデプロイ先はAWSとする。", ["cloud", "aws"], date(2024, 1, 10), "yamada"),
    Record("cloud", "コスト最適化のためGCPへ移行する。", ["cloud", "gcp"], date(2024, 11, 20), "yamada"),
    Record("cloud", "社内のML基盤統合に合わせてAzureに移行する。", ["cloud", "azure"], date(2025, 7, 5), "kimura"),
    Record("review", "コードレビューは必ず2人の承認を必要とする。", ["review", "2approvals"], date(2024, 3, 1), "sato"),
    Record("review", "レビュー負荷が高いため、1人承認+Lintボットの自動チェックに変更する。", ["review", "1approval-bot"], date(2025, 1, 10), "sato"),
    Record("review", "Lintボットを信頼し、人間レビューは1人承認のみで良いとする。", ["review", "1approval"], date(2025, 8, 1), "ito"),
]

QUERIES = [
    ("search", ["search", "elasticsearch"], date(2024, 6, 1), "全文検索基盤はElasticsearchを採用する。"),
    ("search", ["search", "opensearch"], date(2025, 1, 1), "運用コストの都合でElasticsearchからOpenSearchに移行する。"),
    ("search", ["search"], date(2026, 10, 6), "追加クラスタ運用をやめ、Postgres全文検索(tsvector)に一本化する。"),
    ("cloud", ["cloud", "aws"], date(2024, 6, 1), "新規サービスのデプロイ先はAWSとする。"),
    ("cloud", ["cloud", "gcp"], date(2025, 3, 1), "コスト最適化のためGCPへ移行する。"),
    ("cloud", ["cloud"], date(2026, 10, 6), "社内のML基盤統合に合わせてAzureに移行する。"),
    ("review", ["review", "2approvals"], date(2024, 6, 1), "コードレビューは必ず2人の承認を必要とする。"),
    ("review", ["review", "bot"], date(2025, 4, 1), "レビュー負荷が高いため、1人承認+Lintボットの自動チェックに変更する。"),
    ("review", ["review"], date(2026, 10, 6), "Lintボットを信頼し、人間レビューは1人承認のみで良いとする。"),
]


class NonDestructiveMemory:
    """compare_memory.pyと同一ロジック(比較の基準線として再掲)。"""

    def __init__(self, records: list[Record]):
        self.records = list(records)

    def recall(self, topic, query_tags, as_of):
        eligible = [r for r in self.records if r.topic == topic and r.occurred_at <= as_of]
        if not eligible:
            return None
        def score(r):
            return (len(set(r.tags) & set(query_tags)), r.occurred_at)
        return max(eligible, key=score)


class EmbargoedMemory:
    """NonDestructiveMemoryと全く同じ選択ロジックだが、「取り込み締切(ingestion_cutoff)」
    より新しい記録はそもそも保持時点で除外する。実世界でいう「日次バッチ取り込み」
    「承認待ちで未確定の記録」のシミュレーション。as_ofクエリがどんな日付を指定しても、
    締切より新しい記録は絶対に見えない。
    """

    def __init__(self, records: list[Record], ingestion_cutoff: date):
        self.ingestion_cutoff = ingestion_cutoff
        self.records = [r for r in records if r.occurred_at <= ingestion_cutoff]

    def recall(self, topic, query_tags, as_of):
        eligible = [r for r in self.records if r.topic == topic and r.occurred_at <= as_of]
        if not eligible:
            return None
        def score(r):
            return (len(set(r.tags) & set(query_tags)), r.occurred_at)
        return max(eligible, key=score)


def run():
    TODAY = date(2026, 10, 6)
    EMBARGO_DAYS = 500
    cutoff = TODAY - timedelta(days=EMBARGO_DAYS)
    print(f"ingestion_cutoff = {cutoff.isoformat()} (today={TODAY.isoformat()} - {EMBARGO_DAYS}days)\n")

    nondestructive = NonDestructiveMemory(RECORDS)
    embargoed = EmbargoedMemory(RECORDS, ingestion_cutoff=cutoff)

    results = []
    for topic, qtags, as_of, expected in QUERIES:
        n = nondestructive.recall(topic, qtags, as_of)
        e = embargoed.recall(topic, qtags, as_of)
        n_ok = (n is not None and n.content == expected)
        e_ok = (e is not None and e.content == expected)
        results.append((topic, as_of, expected, n, n_ok, e, e_ok))

    print(f"{'topic':<8} {'as_of':<12} {'nondestructive':<16} {'embargoed':<10}")
    for topic, as_of, expected, n, n_ok, e, e_ok in results:
        print(f"{topic:<8} {as_of.isoformat():<12} {'OK' if n_ok else 'NG':<16} {'OK' if e_ok else 'NG':<10}")
        if not e_ok:
            print(f"    期待:         {expected}")
            print(f"    embargo型の回答: {e.content if e else '(該当記録なし)'}")

    n_correct = sum(r[4] for r in results)
    e_correct = sum(r[6] for r in results)
    total = len(results)
    print()
    print(f"nondestructive accuracy: {n_correct}/{total} = {n_correct/total:.1%}")
    print(f"embargoed accuracy:      {e_correct}/{total} = {e_correct/total:.1%}")

    past = [r for r in results if r[1] < TODAY]
    now = [r for r in results if r[1] == TODAY]
    past_e_correct = sum(r[6] for r in past)
    now_e_correct = sum(r[6] for r in now)
    print(f"  内訳: 過去クエリ {past_e_correct}/{len(past)} 、「現在」クエリ {now_e_correct}/{len(now)}")


if __name__ == "__main__":
    run()
