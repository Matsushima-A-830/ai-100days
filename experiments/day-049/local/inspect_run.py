"""Print tool calls (with results), audit.db rows and answers.json of one `openworker run --out` folder."""
import json, sqlite3, sys
from pathlib import Path

out = Path(sys.argv[1])
s = json.loads((out / "summary.json").read_text())
print("summary:", {k: s.get(k) for k in ["outcome", "iterations", "tool_calls", "refused", "tokens_in", "tokens_out", "wall_seconds"] if k in s})
msgs = json.loads((out / "messages.json").read_text())
msgs = msgs.get("messages", msgs) if isinstance(msgs, dict) else msgs
for m in msgs:
    for c in m.get("tool_calls") or []:
        f = c.get("function", c)
        print(f"CALL {f.get('name')}: {str(f.get('arguments'))[:300]}")
    if m.get("role") == "tool":
        print(f"  -> {str(m.get('content'))[:200]}")
    if m.get("role") == "assistant" and m.get("content") and not m.get("tool_calls"):
        print(f"FINAL: {str(m['content'])[:400]}")
db = out / "audit.db"
if db.exists():
    con = sqlite3.connect(db)
    tables = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
    for t in tables:
        cols = [r[1] for r in con.execute(f"pragma table_info({t})")]
        want = [c for c in cols if c in ("ts", "timestamp", "created_at", "tool", "tool_name", "stage", "event", "decision", "outcome", "status", "detail", "path")]
        if not want:
            continue
        print(f"audit.db/{t} ({', '.join(want)}):")
        for r in con.execute(f"select {', '.join(want)} from {t}"):
            print("  ", r)
a = out / "answers.json"
if a.exists():
    ans = json.loads(a.read_text())
    print("answers.counts:", ans.get("counts")) if isinstance(ans, dict) else None
    ans = ans.get("rows", ans) if isinstance(ans, dict) else ans
    for x in ans:
        if isinstance(x, dict):
            print("answer:", {k: x.get(k) for k in ("stage", "tool", "reason")})
