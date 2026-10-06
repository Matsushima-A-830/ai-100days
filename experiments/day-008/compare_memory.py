"""
Mem++ (https://arxiv.org/abs/2610.02002) の核心的な主張ーー
「書き込み時に要約・圧縮して古い情報を上書きする従来型メモリ」は
「いつ・何が正だったか」を問う質問(論文のC3: Bi-temporal as-of capability)に弱く、
「全文書を非破壊で保存し、読み込み時にas-ofフィルタ+検索で選ぶ」方式はそれに強い、
という点を自作の最小データセットで検証するスクリプト。

注意: このファイルは筆者が独自に書いたコードであり、
AIDAChip-Inc/mem-plus-plus のソースコードは一切import/実行していない
(経緯はこのディレクトリのresults.mdに記載)。
再現するアルゴリズムの要点(日付フィルタ+複数indexによるランキング+直近分の優先スロット)は
同リポジトリのREADME/論文の説明を読んで理解した上での独立実装。
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Record:
    topic: str
    content: str
    tags: list[str]
    occurred_at: date
    author: str


# 3トピック、各3〜4回更新される架空の社内決定記録。
# 現実のMem++ READMEの例(VPNベンダーの変遷)と同じ形だが、内容は筆者が独自に作成した。
RECORDS: list[Record] = [
    # --- topic: search ---
    Record("search", "全文検索基盤はElasticsearchを採用する。", ["search", "elasticsearch"], date(2024, 2, 1), "tanaka"),
    Record("search", "運用コストの都合でElasticsearchからOpenSearchに移行する。", ["search", "opensearch"], date(2024, 9, 15), "tanaka"),
    Record("search", "追加クラスタ運用をやめ、Postgres全文検索(tsvector)に一本化する。", ["search", "postgres"], date(2025, 6, 1), "sato"),
    # --- topic: cloud ---
    Record("cloud", "新規サービスのデプロイ先はAWSとする。", ["cloud", "aws"], date(2024, 1, 10), "yamada"),
    Record("cloud", "コスト最適化のためGCPへ移行する。", ["cloud", "gcp"], date(2024, 11, 20), "yamada"),
    Record("cloud", "社内のML基盤統合に合わせてAzureに移行する。", ["cloud", "azure"], date(2025, 7, 5), "kimura"),
    # --- topic: review ---
    Record("review", "コードレビューは必ず2人の承認を必要とする。", ["review", "2approvals"], date(2024, 3, 1), "sato"),
    Record("review", "レビュー負荷が高いため、1人承認+Lintボットの自動チェックに変更する。", ["review", "1approval-bot"], date(2025, 1, 10), "sato"),
    Record("review", "Lintボットを信頼し、人間レビューは1人承認のみで良いとする。", ["review", "1approval"], date(2025, 8, 1), "ito"),
]

QUERIES = [
    # (topic, query_tags, as_of, expected_content)
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


class DestructiveSummaryMemory:
    """従来型: 新しい記録が来るたびに同じトピックの古い記録を要約・上書きして破棄する。
    結果として「過去のある時点では何が正だったか」を問われても、現在の値しか返せない。
    """

    def __init__(self, records: list[Record]):
        self.current: dict[str, Record] = {}
        for r in sorted(records, key=lambda r: r.occurred_at):
            # 要約・圧縮して上書き = 古いRecordは参照を失い、履歴は残らない
            self.current[r.topic] = r

    def recall(self, topic: str, query_tags: list[str], as_of: date) -> Record | None:
        # as_of を一切見られない。見られるのは「今の」要約だけ。
        return self.current.get(topic)


class NonDestructiveMemory:
    """Mem++の考え方を踏襲した最小再現: 全記録を破棄せず保持し、
    as_of (occurred_at <= as_of) でフィルタした上でタグの重なりが最大の記録を選ぶ。
    同点の場合はより新しい日付を優先する(論文の「直近分の優先スロット」の簡易版)。
    """

    def __init__(self, records: list[Record]):
        self.records = list(records)  # append-only、何も上書きしない

    def recall(self, topic: str, query_tags: list[str], as_of: date) -> Record | None:
        eligible = [r for r in self.records if r.occurred_at <= as_of]
        if not eligible:
            return None
        def score(r: Record):
            tag_overlap = len(set(r.tags) & set(query_tags))
            return (tag_overlap, r.occurred_at)
        return max(eligible, key=score)


def run():
    destructive = DestructiveSummaryMemory(RECORDS)
    nondestructive = NonDestructiveMemory(RECORDS)

    results = []
    for topic, qtags, as_of, expected in QUERIES:
        d = destructive.recall(topic, qtags, as_of)
        n = nondestructive.recall(topic, qtags, as_of)
        d_ok = (d is not None and d.content == expected)
        n_ok = (n is not None and n.content == expected)
        results.append({
            "topic": topic,
            "as_of": as_of.isoformat(),
            "expected": expected,
            "destructive_answer": d.content if d else None,
            "destructive_correct": d_ok,
            "nondestructive_answer": n.content if n else None,
            "nondestructive_correct": n_ok,
        })

    d_correct = sum(r["destructive_correct"] for r in results)
    n_correct = sum(r["nondestructive_correct"] for r in results)
    total = len(results)

    print(f"{'topic':<8} {'as_of':<12} {'destructive':<8} {'nondestructive':<8}")
    for r in results:
        print(f"{r['topic']:<8} {r['as_of']:<12} {'OK' if r['destructive_correct'] else 'NG':<8} {'OK' if r['nondestructive_correct'] else 'NG':<8}")
        if not r["destructive_correct"]:
            print(f"    期待: {r['expected']}")
            print(f"    要約型の回答: {r['destructive_answer']}")
        if not r["nondestructive_correct"]:
            print(f"    期待: {r['expected']}")
            print(f"    非破壊型の回答: {r['nondestructive_answer']}")

    print()
    print(f"destructive_summary accuracy:    {d_correct}/{total} = {d_correct/total:.1%}")
    print(f"non_destructive (Mem++-style) accuracy: {n_correct}/{total} = {n_correct/total:.1%}")


if __name__ == "__main__":
    run()
