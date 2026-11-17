"""Hands-on demo of jarvis.memory.db.Database diary storage + FTS5 search.

Real SQLite-backed Database, no mocking. We skip the vector half of the
hybrid search (query_vec_json=None) because that needs an embedding model;
per db.spec.md, a missing source contributes zero to the fused rank and the
search degrades cleanly to FTS5 keyword search, which is what this shows.

Run with:
    PYTHONPATH=/tmp/jarvis-src/src .venv/bin/python demo_diary_search.py
"""
import tempfile
from pathlib import Path

from jarvis.memory.db import Database

with tempfile.TemporaryDirectory() as tmp:
    db_path = str(Path(tmp) / "demo_diary.db")
    db = Database(db_path)

    entries = [
        ("2026-11-10", "User asked how to make cold brew coffee at home, discussed grind size."),
        ("2026-11-12", "User complained about a noisy neighbour's dog barking at night."),
        ("2026-11-14", "User mentioned switching from drip coffee to an espresso machine."),
        ("2026-11-15", "User asked assistant to summarise a long email about rent renewal."),
    ]
    for date, summary in entries:
        sid = db.upsert_conversation_summary(date, summary, topics="diary-demo")
        print(f"upsert_conversation_summary({date}) -> id={sid}")

    print(f"\nhas_vector_store -> {db.has_vector_store}  "
          f"(no embedding backend installed, so this stays keyword-only)")

    query = "coffee"
    rows = db.search_hybrid(fts_query=query, query_vec_json=None, top_k=5)
    print(f"\nsearch_hybrid(fts_query={query!r}, query_vec_json=None) -> {len(rows)} hits:")
    for r in rows:
        print(f"  - score={r['score']:.3f}  {r['text']}")

    db.close()
