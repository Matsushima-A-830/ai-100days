"""Hands-on demo of jarvis.memory.recall_gate.should_recall().

No mocking, no LLM: this calls the real, deterministic heuristic that
decides whether a reply turn needs to hit the diary/graph/memory-digest
recall path, or can skip it because the hot window already covers the
query. Run with:

    PYTHONPATH=/tmp/jarvis-src/src .venv/bin/python demo_recall_gate.py
"""
from jarvis.memory.recall_gate import should_recall

CASES = [
    {
        "name": "fresh tool result + high overlap -> should SKIP recall",
        "query": "What's the weather in Tokyo right now?",
        "recent_messages": [
            {"role": "user", "content": "What's the weather in Tokyo right now?"},
            {
                "role": "user",
                "tool_name": "weather",
                "content": "Tokyo: 18C, light rain, humidity 72%",
            },
        ],
    },
    {
        "name": "fresh tool result but LOW overlap -> should RECALL",
        "query": "Did I mention my sister's birthday last week?",
        "recent_messages": [
            {"role": "user", "content": "What's the weather in Tokyo right now?"},
            {
                "role": "user",
                "tool_name": "weather",
                "content": "Tokyo: 18C, light rain, humidity 72%",
            },
        ],
    },
    {
        "name": "high overlap but NO tool result -> should RECALL",
        "query": "What's the weather in Tokyo right now?",
        "recent_messages": [
            {"role": "user", "content": "What's the weather in Tokyo right now?"},
            {"role": "assistant", "content": "Let me check the weather in Tokyo for you."},
        ],
    },
    {
        "name": "empty hot window -> should RECALL (fail open)",
        "query": "What's the weather in Tokyo right now?",
        "recent_messages": [],
    },
]

for case in CASES:
    result = should_recall(case["query"], case["recent_messages"])
    verb = "SKIP recall" if result is False else "RECALL"
    print(f"- {case['name']}")
    print(f"  query={case['query']!r}")
    print(f"  should_recall() -> {result}  =>  {verb}")
