"""Live demo: jarvis.memory.graph_ops.update_graph_from_dialogue against a
real local LLM (Ollama), no mocking.

This is the part demo_graph_memory.py could not cover: extracting facts from
a conversation summary, choosing the destination node, and merging into it
are all LLM calls. Here they go to a local Ollama server.

Run with (Ollama running locally, model pulled):
    MODEL=gemma4:e4b PYTHONPATH=<jarvis-src>/src .venv/bin/python demo_live_graph_update.py
"""
import os
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

from jarvis.memory.graph import GraphMemoryStore
from jarvis.memory.graph_ops import update_graph_from_dialogue

MODEL = os.environ.get("MODEL", "gemma4:e4b")
cfg = SimpleNamespace(
    llm_provider="ollama",
    ollama_base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
)

SUMMARIES = [
    ("2026-11-10",
     "User said they live in Tokyo and work as a backend engineer using Go. "
     "User prefers black coffee with no sugar. User asked the assistant to "
     "always answer in short bullet points. User also asked what the weather "
     "was like today; it was sunny."),
    ("2026-11-15",
     "User mentioned they moved from Tokyo to Osaka last weekend. "
     "User said they have started drinking oat milk lattes instead of black coffee."),
]


def dump(store: GraphMemoryStore) -> None:
    def walk(node_id: str, depth: int) -> None:
        node = store.get_node(node_id)
        data = (node.data or "").strip().replace("\n", " | ")
        print(f"{'  ' * depth}- {node.name}" + (f": {data}" if data else ""))
        for child in store.get_children(node_id):
            walk(child.id, depth + 1)
    walk("root", 0)


with tempfile.TemporaryDirectory() as tmp:
    store = GraphMemoryStore(str(Path(tmp) / "live_graph.db"))
    print(f"model={MODEL}")
    for date, summary in SUMMARIES:
        t0 = time.time()
        result = update_graph_from_dialogue(
            store, summary, cfg, chat_model=MODEL, timeout_sec=120.0, date_utc=date,
        )
        print(f"\n[{date}] update_graph_from_dialogue -> "
              f"stored={len(result.stored)} skipped={result.skipped} "
              f"({time.time() - t0:.1f}s)")
        for fact, node_name in result.stored:
            print(f"  + {fact!r} -> {node_name}")
        print("graph now:")
        dump(store)
