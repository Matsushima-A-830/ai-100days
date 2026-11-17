"""Hands-on demo of jarvis.memory.graph.GraphMemoryStore.

Real SQLite-backed store, no mocking and no LLM: create_node/append_to_node/
search_nodes/get_top_nodes are the actual production code paths. The only
thing we don't exercise is auto-split (split_node), because triggering it
for real requires an LLM call (see graph_ops.update_graph_from_dialogue) --
this script shows that the token threshold which *decides* whether a split
is due is a plain, callable, local check.

Run with:
    PYTHONPATH=/tmp/jarvis-src/src .venv/bin/python demo_graph_memory.py
"""
import tempfile
from pathlib import Path

from jarvis.memory.graph import (
    GraphMemoryStore,
    BRANCH_USER,
    BRANCH_WORLD,
    SPLIT_THRESHOLD,
    FIXED_BRANCHES,
)

with tempfile.TemporaryDirectory() as tmp:
    db_path = str(Path(tmp) / "demo_graph.db")
    store = GraphMemoryStore(db_path)

    print(f"bootstrap: {store.get_node_count()} nodes "
          f"(root + {len(FIXED_BRANCHES)} fixed branches: "
          f"{[bid for bid, _, _ in FIXED_BRANCHES]})")

    # Create a child under the User branch, as the real extraction pipeline
    # would (graph_ops.update_graph_from_dialogue), minus the LLM call.
    node = store.create_node(
        name="Coffee preference",
        description="What the user likes to drink",
        data="user prefers black coffee, no sugar",
        parent_id=BRANCH_USER,
    )
    print(f"\ncreate_node -> id={node.id[:8]}... data={node.data!r} "
          f"tokens={node.data_token_count}")

    # Append more facts the way append_to_node fallback does on merge failure.
    for fact in [
        "user drinks coffee every morning around 7am",
        "user tried matcha once and disliked the bitterness",
    ]:
        node = store.append_to_node(node.id, fact)
    print(f"after 2 appends: tokens={node.data_token_count} "
          f"(SPLIT_THRESHOLD={SPLIT_THRESHOLD}) "
          f"over_threshold={node.data_token_count > SPLIT_THRESHOLD}")

    # Simulate crossing the split threshold with one big paste, to show the
    # local, LLM-free check that decides a split is due.
    bulk = " ".join(f"fact number {i} about nothing in particular" for i in range(400))
    node = store.append_to_node(node.id, bulk)
    print(f"after bulk append: tokens={node.data_token_count} "
          f"over_threshold={node.data_token_count > SPLIT_THRESHOLD}")

    # A second, unrelated node under World, to test search + access decay.
    world_node = store.create_node(
        name="Local cafe hours",
        description="Opening hours of a place the user asked about",
        data="Blue Bottle Coffee on 5th closes at 6pm on Sundays",
        parent_id=BRANCH_WORLD,
    )

    results = store.search_nodes("coffee")
    print(f"\nsearch_nodes('coffee') -> {len(results)} hits:")
    for r in results:
        print(f"  - {r.name!r} (parent branch via ancestry, data={r.data[:40]!r}...)")

    # search_nodes touches matches, which feeds the decayed access score.
    top = store.get_top_nodes(limit=5)
    print(f"\nget_top_nodes(5) -> {[t.name for t in top]}")

    store.close()
